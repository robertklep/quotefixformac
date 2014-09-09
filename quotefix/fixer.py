from    AppKit                  import NSRunAlertPanel, NSAlternateKeyMask, NSEvent, NSKeyDown, NSControlKeyMask, MessageViewer
from    Foundation              import NSLog
from    quotefix.utils          import swizzle
from    quotefix.attribution    import CustomizedAttribution
from    quotefix.messagetypes   import *
from    objc                    import Category, lookUpClass
from    logger                  import logger
import  re, traceback, objc

DOMText = lookUpClass('DOMText')

MailApp = lookUpClass('MailApp')
class MailApp(Category(MailApp)):

    @classmethod
    def registerQuoteFixApplication(cls, app):
        cls.app = app

    @swizzle(MailApp, 'sendEvent:')
    def sendEvent(self, original, event):
        if not hasattr(self, 'app'):
            original(self, event)
            return
        self.app.toggle_key_active = False
        # keep track of an active option key
        flags = event.modifierFlags()
        if (flags & NSAlternateKeyMask) and not (flags & NSControlKeyMask):
            self.app.toggle_key_active = True
            # handle reply/reply-all (XXX: won't work if you have assigned
            # a different shortcut key to these actions!)
            if event.type() == NSKeyDown and event.charactersIgnoringModifiers().lower() == 'r':
                # strip the Option-key from the event
                event = NSEvent.keyEventWithType_location_modifierFlags_timestamp_windowNumber_context_characters_charactersIgnoringModifiers_isARepeat_keyCode_(
                    event.type(),
                    event.locationInWindow(),
                    event.modifierFlags() & ~NSAlternateKeyMask,
                    event.timestamp(),
                    event.windowNumber(),
                    event.context(),
                    event.characters(),
                    event.charactersIgnoringModifiers(),
                    event.isARepeat(),
                    event.keyCode()
                )
        original(self, event)

# our own DocumentEditor implementation
DocumentEditor = lookUpClass('DocumentEditor')
class DocumentEditor(Category(DocumentEditor)):

    @classmethod
    def registerQuoteFixApplication(cls, app):
        cls.app = app

    @swizzle(DocumentEditor, 'finishLoadingEditor')
    def finishLoadingEditor(self, original):
        logger.debug('DocumentEditor finishLoadingEditor')

        # execute original finishLoadingEditor()
        original(self)

        try:
            # if toggle key is active, temporarily switch the active state
            is_active = self.app.toggle_key_active ^ self.app.is_active

            # check if we can proceed
            if not is_active:
                logger.debug("QuoteFix is not active, so no QuoteFixing for you!")
                return

            # grab composeView instance (this is the WebView which contains the
            # message editor) and check for the right conditions
            try:
                view = objc.getInstanceVariable(self, 'composeWebView')
            except:
                # was renamed in Lion
                view = objc.getInstanceVariable(self, '_composeWebView')

            # grab some other variables we need to perform our business
            backend     = self.backEnd()
            htmldom     = view.mainFrame().DOMDocument()
            htmlroot    = htmldom.documentElement()
            messageType = self.messageType()

            # XXX: hack alert! if message type is DRAFT, but we can determine this
            # is actually a Send Again action, adjust the message type.
            origmsg = backend.originalMessage()
            if origmsg and messageType == DRAFT:
                # get the message viewer for this message
                viewer = MessageViewer.existingViewerShowingMessage_(origmsg)
                if not viewer:
                    # XXX: this happens with conversation view active, not sure if this is stable enough though
                    messageType = SENDAGAIN
                elif viewer:
                    # get the mailbox for the viewer
                    mailboxes = viewer.selectedMailboxes()
                    # get the Drafts mailbox
                    draftmailbox = viewer.draftsMailbox()
                    # check if they're the same; if not, it's a Send-Again
                    if draftmailbox not in mailboxes:
                        messageType = SENDAGAIN

            # send original HTML to menu for debugging
            self.app.html = htmlroot.innerHTML()

            # provide custom attribution?
            attributor = None
            if self.app.use_custom_reply_attribution and messageType in [ REPLY, REPLY_ALL, REPLY_AS ]:
                logger.debug("calling customize_attribution() for reply{-all,-as}")
                attributor = CustomizedAttribution.customize_reply
            elif self.app.use_custom_sendagain_attribution and messageType in [ SENDAGAIN ]:
                logger.debug("calling customize_attribution() for Send Again")
                attributor = CustomizedAttribution.customize_sendagain
            elif self.app.use_custom_forwarding_attribution and messageType == FORWARD:
                logger.debug("calling customize_attribution() for forwarding")
                attributor = CustomizedAttribution.customize_forward

            if attributor:
                # play nice with Attachment Tamer
                try:
                    message = backend.draftMessage()
                except:
                    message = backend._makeMessageWithContents_isDraft_shouldSign_shouldEncrypt_shouldSkipSignature_shouldBePlainText_(
                        backend.copyOfContentsForDraft_shouldBePlainText_isOkayToForceRichText_(True, False, True),
                        True,
                        False,
                        False,
                        False,
                        False
                    )
                try:
                    for original in objc.getInstanceVariable(backend, '_originalMessages'):
                        attributor(
                            app         = self.app,
                            editor      = self,
                            dom         = htmldom,
                            reply       = message,
                            inreplyto   = original,
                        )
                    backend.setHasChanges_(False)
                except:
                    # ignore when not debugging
                    if self.app.is_debugging:
                        raise

            # should we be quotefixing?
            if not self.app.is_quotefixing:
                logger.debug('quotefixing turned off in preferences, skipping that part')
            elif messageType not in self.app.message_types_to_quotefix:
                logger.debug('message type "%s" not in %s, not quotefixing' % (
                    messageType,
                    self.app.message_types_to_quotefix
                ))
            else:
                # remove attachment placeholders?
                if self.app.remove_attachment_placeholders:
                    self.remove_attachment_placeholders(backend, htmlroot)
                    backend.setHasChanges_(False)

                # move cursor to end of document
                view.moveToEndOfDocument_(self)

                # remove quotes?
                if self.app.remove_quotes:
                    logger.debug('calling remove_quotes()')
                    self.remove_quotes(htmldom, self.app.remove_quotes_level)
                    backend.setHasChanges_(False)

                # make quotes selectable?
                if self.app.selectable_quotes:
                    logger.debug('calling make_selectable_quotes()')
                    self.make_selectable_quotes(view, htmldom)
                    backend.setHasChanges_(False)

                # remove signature from sender
                if not self.app.keep_sender_signature:
                    logger.debug('calling remove_old_signature()')
                    if self.remove_old_signature(htmldom, view):
                        backend.setHasChanges_(False)

                # place cursor above own signature (if any)
                logger.debug('calling move_above_new_signature()')
                if self.move_above_new_signature(htmldom, view):
                    backend.setHasChanges_(False)
                else:
                    view.insertNewline_(self)

                # perform some general cleanups
                logger.debug('calling cleanup_layout()')
                if self.cleanup_layout(htmlroot, backend):
                    backend.setHasChanges_(False)

                # move cursor to end of document
                if self.app.move_cursor_to_top:
                    view.moveToBeginningOfDocument_(self)

            # move to beginning of line
            logger.debug('calling view.moveToBeginningOfLine()')
            view.moveToBeginningOfLine_(self)

            # done
            logger.debug('QuoteFixing done')
        except Exception:
            logger.critical(traceback.format_exc())
            if self.app.is_debugging:
                NSRunAlertPanel(
                    'QuoteFix caught an exception',
                    'The QuoteFix plug-in caught an exception:\n\n' +
                    traceback.format_exc() +
                    '\nPlease contact the developer quoting the contents of this alert.',
                    None, None, None
                )

    def remove_attachment_placeholders(self, backend, htmlroot):
        messages = objc.getInstanceVariable(backend, '_originalMessages')
        for original in messages:
            messagebody = original.messageBody()
            if not messagebody:
                return
            attachments = messagebody.attachmentFilenames()
            if not attachments:
                return
            html        = htmlroot.innerHTML()
            matchnames  = []
            for attachment in attachments:
                attachment  = attachment.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                escaped     = re.escape('&lt;%s&gt;' % attachment)
                escaped     = escaped.replace(r'\ ', r'(?: |\&nbsp;)')
                escaped     = escaped.replace(r'\:', '[:_]')
                matchnames.append(escaped)
            matches = "|".join(matchnames)
            html    = re.sub(matches, '', html)
            htmlroot.setInnerHTML_(html)

    def remove_quotes(self, dom, level):
        # find all blockquotes
        blockquotes = dom.querySelectorAll_("blockquote")
        for i in range(blockquotes.length()):
            blockquote = blockquotes.item_(i)
            # check quotelevel against maximum allowed level
            if blockquote.quoteLevel() >= level:
                blockquote.parentNode().removeChild_(blockquote)

    def make_selectable_quotes(self, view, dom):
        return

        # find all blockquotes
        blockquotes = dom.querySelectorAll_("blockquote")
        for i in range(blockquotes.length()):
            blockquote = blockquotes.item_(i)
            # don't fix top-level blockquote
            if blockquote.quoteLevel() > 1:
                # get current computed style
                style = dom.getComputedStyle_pseudoElement_(blockquote, None).cssText()

                # remove text-color-related stuff (so it will be inherited)
                style = re.sub(r'\scolor.*?:.*?;', '', style)
                style = re.sub(r'\soutline-color.*?:.*?;', '', style)
                style = re.sub(r'\s-webkit-text-emphasis-color.*?:.*?;', '', style)
                style = re.sub(r'\s-webkit-text-fill-color.*?:.*?;', '', style)
                style = re.sub(r'\s-webkit-text-stroke-color.*?:.*?;', '', style)
                style = re.sub(r'\sflood-color.*?:.*?;', '', style)
                style = re.sub(r'\slighting-color.*?:.*?;', '', style)

                # remove 'type' attribute
                blockquote.removeAttribute_("type")

                # and set style attribute to match original style
                blockquote.setAttribute_value_("style", style)

    # try to find, and remove, signature of sender
    def remove_old_signature(self, dom, view):
        signature   = None
        root        = dom.documentElement()

        # grab first blockquote (if any)
        blockquote = root.firstDescendantBlockQuote()
        if not blockquote:
            return False

        # get matcher
        matcher = self.app.signature_matcher

        # find nodes which might contain senders signature
        nodes   = []
        matches = dom.querySelectorAll_("div, br, span")
        nodes   += [ matches.item_(i) for i in range(matches.length()) ]

        # try to find a signature
        matches = []
        for node in nodes:
            # skip nodes which aren't at quotelevel 1
            if node.quoteLevel() != 1:
                continue

            # BR's are empty, so treat them differently
            if node.nodeName().lower() == 'br':
                nextnode = node.nextSibling()
                if isinstance(nextnode, DOMText) and matcher.search(nextnode.data()):
                    matches.append(node)
            elif node.nodeName().lower() in [ 'div', 'span' ] and matcher.search(node.innerHTML()):
                matches.append(node)

        # if we found a signature, remove it
        if len(matches):
            signature = matches[self.app.remove_from_last_signature_match and -1 or 0]

            # remove all siblings following signature, except for attachments
            node    = signature
            parent  = signature.parentNode()
            while node:
                if node.nodeName().lower() == 'object':
                    node = node.nextSibling()
                else:
                    nextnode = node.nextSibling()
                    parent.removeChild_(node)
                    node = nextnode
                while not node and parent != blockquote:
                    node    = parent.nextSibling()
                    parent  = parent.parentNode()

            # move down a line
            view.moveDown_(self)

            # and insert a paragraph break
            view.insertParagraphSeparator_(self)

            # remove empty lines
            blockquote.removeStrayLinefeeds()

            # signal that we removed an old signature
            return True

        # found nothing?
        return False

    def move_above_new_signature(self, dom, view):
        # find new signature by ID
        div = dom.getElementById_("AppleMailSignature")
        if not div:
            return False

        # set selection range
        domrange = dom.createRange()
        domrange.selectNode_(div)

        # create selection
        view.setSelectedDOMRange_affinity_(domrange, 0)

        # move up (positions cursor above signature)
        view.moveUp_(self)

        # insert a paragraph break?
        if not self.app.no_whitespace_below_quote:
            view.insertParagraphSeparator_(self)

        # signal that we moved
        return True

    def cleanup_layout(self, root, backend):
        # clean up stray linefeeds
        if not self.app.keep_leading_whitespace:
            root.getElementsByTagName_("body").item_(0)._removeStrayLinefeedsAtBeginning()

        # remove trailing whitespace on first blockquote?
        if self.app.remove_trailing_whitespace:
            blockquote = root.firstDescendantBlockQuote()
            if blockquote:
                blockquote._removeStrayLinefeedsAtEnd()

        # done?
        if self.app.keep_attribution_whitespace:
            return True

        # clean up linebreaks before first blockquote
        blockquote = root.firstDescendantBlockQuote()
        if blockquote:
            parent  = blockquote.parentNode()
            node    = blockquote.previousSibling()
            while node and node.nodeName().lower() == 'br':
                parent.removeChild_(node)
                node = blockquote.previousSibling()

        return True

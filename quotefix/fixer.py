from    AppKit                  import NSRunAlertPanel, NSAlternateKeyMask, NSEvent, NSKeyDown, NSFlagsChanged, NSControlKeyMask, MessageViewer
from    Foundation              import NSLog
from    quotefix.utils          import swizzle
from    quotefix.attribution    import CustomizedAttribution
from    quotefix.messagetypes   import *
from    objc                    import Category, lookUpClass
from    logger                  import logger
import  re, traceback, objc

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

        # Keep track of an active Opt key
        if event.type() == NSFlagsChanged:
            flags = event.modifierFlags()
            self.app.toggle_key_active = (flags & NSAlternateKeyMask) and not (flags & NSControlKeyMask)

        # Handle reply/reply-all (XXX: won't work if you have assigned a different shortcut key to these actions)
        if self.app.toggle_key_active and event.type() == NSKeyDown and event.charactersIgnoringModifiers().lower() == 'r':
            # Strip the Opt-key from the event
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

def fix(self):
    try:
        # if toggle key is active, temporarily switch the active state
        is_active = self.app.toggle_key_active ^ self.app.is_active

        # check if we can proceed
        if not is_active:
            logger.debug("QuoteFix is not active, so no QuoteFixing for you!")
            return

        # Grab some variables we need to perform our business
        view        = self.composeWebView() # contains the message editor
        backend     = self.backEnd()
        htmldom     = view.mainFrame().DOMDocument()
        htmlroot    = htmldom.documentElement()
        messageType = self.messageType()

        # XXX: hack alert! if message type is DRAFT, but we can determine this
        # is actually a Send Again action, adjust the message type.
        origmsg = backend.originalMessage()
        if origmsg and messageType == DRAFT and origmsg.type() == 0:
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
            try:
                for original in objc.getInstanceVariable(backend, '_originalMessages'):
                    attributor(
                        app       = self.app,
                        editor    = self,
                        dom       = htmldom,
                        reply     = backend.message(),
                        inreplyto = original,
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
                logger.debug('calling remove_attachment_placeholders()')
                self.remove_attachment_placeholders(backend, htmlroot)

            # move cursor to end of document
            view.moveToEndOfDocument_(self)

            # remove quotes?
            if self.app.remove_quotes:
                logger.debug('calling remove_quotes()')
                self.remove_quotes(htmldom, self.app.remove_quotes_level)

            # make quotes selectable?
            if self.app.selectable_quotes:
                logger.debug('calling make_selectable_quotes()')
                self.make_selectable_quotes(view, htmldom)

            # remove signature from sender
            if not self.app.keep_sender_signature:
                logger.debug('calling remove_old_signature()')
                self.remove_old_signature(htmldom, view)

            # place cursor above own signature (if any)
            logger.debug('calling move_above_new_signature()')
            if self.move_above_new_signature(htmldom, view):
                # insert a paragraph break?
                if not self.app.no_whitespace_below_quote:
                    view.insertParagraphSeparator_(self)
            else:
                view.insertNewline_(self)

            # perform some general cleanups
            logger.debug('calling cleanup_layout()')
            self.cleanup_layout(htmlroot, backend)

            # move cursor to top of document
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
    if not messages:
        NSLog('unable to retrieve _originalMessages')
        return
    for original in messages:
        if original.respondsToSelector_('parsedMessage'):
            # Sierra
            message = original.parsedMessage()
            attachments = [ v.filename() for k, v in message.attachmentsByURL().iteritems() ]
        elif original.respondsToSelector_('messageBody'):
            messagebody = original.messageBody()
            if not messagebody:
                # High Sierra
                NSLog('unable to retrieve message body to remove attachment placeholders')
                continue
            else:
                # ElCap and older
                attachments = messagebody.attachmentFilenames()
        else:
            NSLog("unable to retrieve list of attachments")
            continue

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

    # find all text nodes
    xpathresult = dom.evaluate_contextNode_resolver_type_inResult_(
        '//text()',
        root,
        None,
        0,
        None
    )
    matches = []
    node = xpathresult.iterateNext()
    while node:
        # if a text node is at quote level 1, and it matches our signature
        # matcher, we'll use it as the start of a signature
        if node.quoteLevel() == 1 and matcher.search(node.data()):
            matches.append(node)
        node = xpathresult.iterateNext()

    # if we found possible signatures, remove them
    if len(matches):
        signature = matches[self.app.remove_from_last_signature_match and -1 or 0]

        # remove all siblings following signature, except for attachments
        node    = signature
        parent  = signature.parentNode()
        while node:
            if node.nodeName().lower() == 'object': # attachment
                node = node.nextSibling()
            else:
                nextnode = node.nextSibling()
                parent.removeChild_(node)
                node = nextnode
            while not node and parent != blockquote:
                node   = parent.nextSibling()
                parent = parent.parentNode()

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
        parent = blockquote.parentNode()
        node   = blockquote.previousSibling()
        while node and node.nodeName().lower() == 'br':
            parent.removeChild_(node)
            node = blockquote.previousSibling()

    return True

# Check which class we need to overload (ComposeViewController for El Capitan,
# DocumentEditor for Yosemite and earlier
try:

    ComposeViewController = lookUpClass('ComposeViewController')
    class ComposeViewController(Category(ComposeViewController)):

        @classmethod
        def registerQuoteFixApplication(cls, app):
            cls.app = app

        @swizzle(ComposeViewController, 'finishLoadingEditor', '_finishLoadingEditor')
        def finishLoadingEditor(self, original):
            logger.debug('[ComposeViewController finishLoadingEditor]')
            original(self)
            self.fix()
            # Don't let any changes made during quotefixing trigger the 'Save
            # to Drafts' alert.
            self.setHasUserMadeChanges_(False)
            self.backEnd().setHasChanges_(False)

        @swizzle(ComposeViewController, 'show')
        def show(self, original):
            logger.debug('[ComposeViewController show]')
            original(self)

            # If toggle key is active, temporarily switch the active state
            is_active = self.app.toggle_key_active ^ self.app.is_active
            if not is_active:
                return

            # When the compose view should be shown, we assume any animations
            # are done and we can position the cursor.
            view    = self.composeWebView()
            htmldom = view.mainFrame().DOMDocument()
            if self.app.move_cursor_to_top:
                view.moveToBeginningOfDocument_(self)
            elif not self.move_above_new_signature(htmldom, view):
                view.moveToEndOfDocument_(self)

    ComposeViewController.fix                            = fix
    ComposeViewController.remove_attachment_placeholders = remove_attachment_placeholders
    ComposeViewController.remove_quotes                  = remove_quotes
    ComposeViewController.make_selectable_quotes         = make_selectable_quotes
    ComposeViewController.remove_old_signature           = remove_old_signature
    ComposeViewController.move_above_new_signature       = move_above_new_signature
    ComposeViewController.cleanup_layout                 = cleanup_layout
except Exception, e:
    logger.debug('Unable to fix ComposeViewController: %s' % e)
    class ComposeViewController:
        @classmethod
        def registerQuoteFixApplication(cls, app):
            cls.app = app

try:
    DocumentEditor = lookUpClass('DocumentEditor')
    class DocumentEditor(Category(DocumentEditor)):
        @classmethod
        def registerQuoteFixApplication(cls, app):
            cls.app = app

        @swizzle(DocumentEditor, 'finishLoadingEditor')
        def finishLoadingEditor(self, original):
            logger.debug('DocumentEditor finishLoadingEditor')
            original(self)
            self.fix()

    DocumentEditor.fix                            = fix
    DocumentEditor.remove_attachment_placeholders = remove_attachment_placeholders
    DocumentEditor.remove_quotes                  = remove_quotes
    DocumentEditor.make_selectable_quotes         = make_selectable_quotes
    DocumentEditor.remove_old_signature           = remove_old_signature
    DocumentEditor.move_above_new_signature       = move_above_new_signature
    DocumentEditor.cleanup_layout                 = cleanup_layout
except Exception, e:
    logger.debug('Unable to fix DocumentEditor: %s' % e)
    class DocumentEditor:
        @classmethod
        def registerQuoteFixApplication(cls, app):
            cls.app = app

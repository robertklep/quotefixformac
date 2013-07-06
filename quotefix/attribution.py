from    AppKit                      import *
from    objc                        import Category, lookUpClass
from    datetime                    import datetime
from    quotefix.utils              import swizzle, SimpleTemplate
from    quotefix.pyratemp           import Template
from    quotefix.messagetypes       import *
from    quotefix.attributionclasses import *
import  re

# patch MessageHeaders class to return empty attributions with forwards
MessageHeaders = lookUpClass('MessageHeaders')
class MessageHeaders(Category(MessageHeaders)):

    @classmethod
    def registerQuoteFixApplication(cls, app):
        cls.app = app

    @swizzle(MessageHeaders, 'htmlStringShowingHeaderDetailLevel:useBold:useGray:')
    def htmlStringShowingHeaderDetailLevel_useBold_useGray_(self, original, level, bold, gray):
        if self.app.use_custom_forwarding_attribution and self.app.remove_apple_mail_forward_attribution:
            return ''
        return original(self, level, bold, gray)

class CustomizedAttribution:
    """ Provide customized reply/sendagain/forward attributions """

    @classmethod
    def registerQuoteFixApplication(cls, app):
        cls.app = app

    @classmethod
    def customize_reply(cls, app, editor, dom, reply, inreplyto):
        return cls.customize_attribution(
            # grab the original attribution string from the
            # Message class, so we can replace it with a
            # customized version of it.
            original    = Message.replyPrefixWithSpacer_(False),
            editor      = editor,
            dom         = dom,
            reply       = reply,
            inreplyto   = inreplyto,
            template    = app.custom_reply_attribution,
            messagetype = REPLY
        )

    @classmethod
    def customize_sendagain(cls, app, editor, dom, reply, inreplyto):
        return cls.customize_attribution(
            original    = Message.replyPrefixWithSpacer_(False),
            editor      = editor,
            dom         = dom,
            reply       = reply,
            inreplyto   = inreplyto,
            template    = app.custom_sendagain_attribution,
            messagetype = SENDAGAIN
        )

    @classmethod
    def customize_forward(cls, app, editor, dom, reply, inreplyto):
        return cls.customize_attribution(
            original    = Message.forwardedMessagePrefixWithSpacer_(False),
            editor      = editor,
            dom         = dom,
            reply       = reply,
            inreplyto   = inreplyto,
            template    = app.custom_forwarding_attribution,
            messagetype = FORWARD
        )

    @classmethod
    def customize_attribution(cls, original, editor, dom, reply, inreplyto, template, messagetype):
        is_forward      = messagetype == FORWARD
        is_reply        = messagetype == REPLY
        is_sendagain    = messagetype == SENDAGAIN

        # create matcher for matching original attribution (and replace
        # nsbp's with normal spaces)
        original    = original.replace(u'\xa0', ' ').strip()
        original    = original.replace('(', r'\(').replace(')', r'\)')
        original    = re.sub(r'%\d+\$\@', '.*?', original)
        matcher     = re.compile(original)

        # find possible nodes which can contain attribution
        root    = dom.documentElement()
        nodes   = root.getElementsByClassName_('AppleOriginalContents')
        if not nodes.length():
            nodes = root.getElementsByClassName_('ApplePlainTextBody')
            if not nodes.length():
                return False
        node = nodes.item_(0)

        # check children for attribution node
        is_rich     = editor.backEnd().containsRichText()
        children    = node.childNodes()
        for i in range(children.length()):
            child = children.item_(i)
            if child.nodeType() == 1:
                html = child.innerHTML()
                if not matcher.match(html):
                    continue
            elif child.nodeType() == 3:
                text = child.data()
                if not matcher.match(text):
                    continue

            # should attribution be treated as HTML?
            is_html =   (is_forward     and cls.app.custom_forwarding_is_html) or \
                        (is_sendagain   and cls.app.custom_sendagain_is_html) or \
                        (is_reply       and cls.app.custom_reply_is_html)

            # check if message is rich text with HTML-attribution
            if is_html and not is_rich:
                if  (is_forward     and cls.app.custom_forwarding_convert_to_rich) or \
                    (is_sendagain   and cls.app.custom_sendagain_convert_to_rich) or \
                    (is_reply       and cls.app.custom_reply_convert_to_rich):
                    editor.makeRichText_(editor)
                elif not cls.app.dont_show_html_attribution_warning:
                    idx = NSRunAlertPanel(
                        "QuoteFix warning",
                        "You are using an HTML-attribution, but the current message format is plain text.\n\n" +
                        "Unless you convert to rich text, the HTML-formatting will be lost when sending the message.",
                        "OK",
                        "Don't show this warning again",
                        None
                    )
                    if idx == 0:
                        cls.app.dont_show_html_attribution_warning = True

            # render attribution
            attribution = cls.render_attribution(
                reply       = reply,
                inreplyto   = inreplyto,
                template    = template,
                is_html     = is_html,
            )

            # replace leading whitespace with non-breaking spaces
            attribution = re.sub(r'(?m)^( +)' , lambda m: u'\u00a0' * len(m.group(1)), attribution)
            attribution = re.sub(r'(?m)^(\t+)', lambda m: u'\u00a0\u00a0' * len(m.group(1)), attribution)

            # replace newlines with hard linebreaks
            attribution = attribution.replace('\n', '<br/>')

            # replace old attribution with new, depending on node type
            if child.nodeType() == 1:
                child.setInnerHTML_(attribution)
                copynode = child
            else:
                newnode = dom.createElement_("span")
                newnode.setInnerHTML_(attribution)
                node.replaceChild_oldChild_(newnode, child)
                copynode = newnode

            # increase quote level of attribution?
            if  (is_forward     and cls.app.custom_forwarding_increase_quotelevel) or \
                (is_sendagain   and cls.app.custom_sendagain_increase_quotelevel) or \
                (is_reply       and cls.app.custom_reply_increase_quotelevel):
                copy = copynode.cloneNode_(True)
                copynode.parentNode().removeChild_(copynode)
                blockquote = root.firstDescendantBlockQuote()
                blockquote.insertBefore_refChild_(copy, blockquote.childNodes().item_(0))

            # done
            return True

        # done nothing
        return False

    @classmethod
    def render_attribution(cls, reply, inreplyto, template, is_html):
        # expand template and return it
        return cls.render_with_params(
            template,
            cls.setup_params(reply, inreplyto),
            is_html
        )

    @classmethod
    def render_with_params(cls, template, params, is_html):
        # hmm...
        template = template.replace('message.from',     'message.From')
        template = template.replace('response.from',    'response.From')
        template = template.replace('recipients.all',   'recipients.All')

        # escape some characters when not using HTML-mode
        if not is_html:
            template = template.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # templating enabled?
        if cls.app.custom_attribution_allow_templating:
            # try to expand a complex template first
            try:
                return Template(string = template, data = params)()
            except Exception, e:
                return "<i>&lt;A templating error occured, please check your template for errors&gt;</i>"

        # simple template
        return SimpleTemplate(template).substitute(params)

    @classmethod
    def setup_params(cls, reply, inreplyto):
        return {
            'message'   : QFMessage(inreplyto),
            'response'  : QFMessage(reply),
            # 'now'?
        }

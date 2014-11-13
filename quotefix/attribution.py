from    AppKit                      import NSRunAlertPanel
from    objc                        import Category, lookUpClass
from    datetime                    import datetime
from    quotefix.utils              import swizzle, SimpleTemplate
from    quotefix.pyratemp           import Template
from    quotefix.messagetypes       import *
from    quotefix.attributionclasses import *
import  re, platform

# Mavericks
try:
    Message = lookUpClass('MCMessage')
except:
    from AppKit import Message

# patch MessageHeaders class to return empty attributions with forwards
try:
    MCMessageHeaders = lookUpClass('MCMessageHeaders')
    class MCMessageHeaders(Category(MCMessageHeaders)):

        @classmethod
        def registerQuoteFixApplication(cls, app):
            cls.app = app

        try:
            @swizzle(MCMessageHeaders, 'htmlStringShowingHeaderDetailLevel:useBold:useGray:')
            def htmlStringShowingHeaderDetailLevel_useBold_useGray_(self, original, level, bold, gray):
                if self.app.use_custom_forwarding_attribution and self.app.remove_apple_mail_forward_attribution:
                    return ''
                return original(self, level, bold, gray)
        except:
            # Yosemite
            @swizzle(MCMessageHeaders, 'htmlStringUseBold:useGray:')
            def htmlStringUseBold_useGray_(self, original, bold, gray):
                if self.app.use_custom_forwarding_attribution and self.app.remove_apple_mail_forward_attribution:
                    return ''
                return original(self, bold, gray)
    MessageHeaders = MCMessageHeaders
except:
    from AppKit import MessageHeaders
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
            original    = None,
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
        if original:
            original = original.replace(u'\xa0', ' ').strip()
            original = original.replace('(', r'\(').replace(')', r'\)')
            original = re.sub(r'%\d+\$\@', '.*?', original)
            original = re.sub(r'\s+', '(?:\\s|&nbsp;)+', original)
            original = original + r'(?=[<\s])'
            matcher  = re.compile(original)
        else:
            matcher = None

        # rich text message?
        is_rich = editor.backEnd().containsRichText()

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

        # Get HTML contents of e-mail.
        root = dom.documentElement()
        html = root.innerHTML()

        # Fix Yosemite attributions
        osversion = platform.mac_ver()[0]
        if osversion.startswith('10.10'):
            # move <blockquote> one level down
            html = re.sub(r'(?i)(<blockquote.*?>)(.*?)(<br.*?>)+', r'\2\1', html, count = 1)

        # Special case: Mail doesn't include an attribution for Send Again messages,
        # so we'll just add a customized attribution right after the <body> element.
        if is_sendagain or matcher == None:
            # TODO: limit quote level!
            html = re.sub(r'(?i)(?P<element><\s?body.*?>)', r'\g<element>' + attribution, html, count = 1)
        elif matcher:
            html = matcher.sub(attribution, html, count = 1)

        # Restore HTML of root element.
        root.setInnerHTML_(html)

        # TODO: increase quote level of attribution?
#        if  (is_forward     and cls.app.custom_forwarding_increase_quotelevel) or \
#            (is_reply       and cls.app.custom_reply_increase_quotelevel):
#            copy = copynode.cloneNode_(True)
#            copynode.parentNode().removeChild_(copynode)
#            blockquote = root.firstDescendantBlockQuote()
#            blockquote.insertBefore_refChild_(copy, blockquote.childNodes().item_(0))

        return True

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
            except Exception:
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

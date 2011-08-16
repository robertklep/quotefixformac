from    AppKit                      import *
from    objc                        import Category, lookUpClass
from    datetime                    import datetime
from    quotefix.utils              import swizzle, SimpleTemplate
from    quotefix.pyratemp           import Template
from    quotefix.attributionclasses import *
import  re

class CustomizedAttribution:
    """ Provide customized reply/forward attributions """

    @classmethod
    def registerQuoteFixApplication(cls, app):
        cls.app = app

    @classmethod
    def customize_reply(cls, app, dom, reply, inreplyto):
        return cls.customize_attribution(
            # grab the original attribution string from the
            # Message class, so we can replace it with a
            # customized version of it.
            original    = Message.replyPrefixWithSpacer_(False),
            dom         = dom,
            reply       = reply,
            inreplyto   = inreplyto,
            template    = app.custom_reply_attribution,
            is_forward  = False
        )

    @classmethod
    def customize_forward(cls, app, dom, reply, inreplyto):
        return cls.customize_attribution(
            original    = Message.forwardedMessagePrefixWithSpacer_(False),
            dom         = dom,
            reply       = reply,
            inreplyto   = inreplyto,
            template    = app.custom_forwarding_attribution,
            is_forward  = True
        )

    @classmethod
    def customize_attribution(cls, original, dom, reply, inreplyto, template, is_forward):
        # create matcher for matching original attribution
        matcher = re.compile(re.sub(r'%\d+\$\@', '.*?', original.strip()))

        # find parent of first quote
        root = dom.documentElement()
        node = root.firstDescendantBlockQuote().parentNode()
        if not node:
            return False

        # check children for attribution node
        children = node.childNodes()
        for i in range(children.length()):
            child = children.item_(i)
            if child.nodeType() == 1 and not matcher.match(child.innerHTML()):
                continue
            elif child.nodeType() == 3 and not matcher.match(child.data()):
                continue

            # render attribution
            attribution = cls.render_attribution(
                reply       = reply,
                inreplyto   = inreplyto,
                template    = template,
            )

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
            if (is_forward and cls.app.custom_forwarding_increase_quotelevel) or (not is_forward and cls.app.custom_reply_increase_quotelevel):
                copy = copynode.cloneNode_(True)
                copynode.parentNode().removeChild_(copynode)
                blockquote = root.firstDescendantBlockQuote()
                blockquote.insertBefore_refChild_(copy, blockquote.childNodes().item_(0))

            # done
            return True

        # done nothing
        return False

    @classmethod
    def render_attribution(cls, reply, inreplyto, template):
        # expand template and return it
        return cls.render_with_params(
            template, 
            cls.setup_params(reply, inreplyto)
        )

    @classmethod
    def render_with_params(cls, template, params):
        # hmm...
        template = template.replace('message.from',     'message.From')
        template = template.replace('response.from',    'response.From')
        template = template.replace('recipients.all',   'recipients.All')

        # templating enabled?
        if cls.app.custom_attribution_allow_templating:
            # try to expand a complex template first
            try:
                return Template(string = template, data = params)()
            except Exception, e:
                pass

        # simple template
        attribution = SimpleTemplate(template).substitute(params)

        # encode (some) entities
        return attribution.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    @classmethod
    def setup_params(cls, reply, inreplyto):
        return {
            'message'   : QFMessage(inreplyto),
            'response'  : QFMessage(reply),
            # 'now'?
        }

from    AppKit              import *
from    objc                import Category, lookUpClass
from    datetime            import datetime
from    quotefix.utils      import swizzle, Template
import  re, email.utils

Message = lookUpClass('Message')

class CustomizedAttribution:
    """ Provide customized reply/forward attributions """

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

            # encode (some) entities
            attribution = attribution.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            # replace newlines with hard linebreaks
            attribution = attribution.replace('\n', '<br/>')

            # replace old attribution with new, depending on node type
            if child.nodeType() == 1:
                child.setInnerHTML_(attribution)
            else:
                newnode = dom.createElement_("span")
                newnode.setInnerHTML_(attribution)
                node.replaceChild_oldChild_(newnode, child)

            # done
            return True

        # done nothing
        return False

    @classmethod
    def render_attribution(cls, reply, inreplyto, template):
        # setup template parameters
        params = {
            'message.from'          : inreplyto.sender(),
            'message.from.name'     : '',
            'message.from.email'    : '',
            'message.sender'        : inreplyto.sender(),
            'message.comment'       : inreplyto.senderAddressComment(),
            'message.to'            : inreplyto.to(),
            'message.subject'       : inreplyto.subject(),
            'response.from'         : reply.sender(),
            'response.from.name'    : '',
            'response.from.email'   : '',
            'response.sender'       : reply.sender(),
            'response.comment'      : reply.senderAddressComment(),
            'response.to'           : reply.to(),
            'response.subject'      : reply.subject(),
        }

        # add dates
        params.update(cls.expand_nsdate(inreplyto.dateSent(),        'message.sent'))
        params.update(cls.expand_nsdate(inreplyto.dateReceived(),    'message.received'))
        params.update(cls.expand_datetime(datetime.now(),            'now'))

        # flatten NSArray-typed parameters
        for k, v in params.items():
            if isinstance(v, NSArray):
                params[k] = v.componentsJoinedByString_(", ")

        # try to split e-mail address from *.from
        for k in [ 'message.from', 'response.from' ]:
            try:    
                params[k + '.name'], params[k + '.email'] = email.utils.parseaddr(params[k])
                # if name is empty, fill it with '.email'
                if not params[k + '.name']:
                    params[k + '.name'] = params[k + '.email']
            except:
                pass

        # expand template and return it
        return Template(template).substitute(params).encode('utf-8')

    # expand an NSDate object to a dictionary
    @classmethod
    def expand_nsdate(cls, nsdate, prefix):
        # convert NSDate to datetime
        date = datetime.strptime(nsdate.description()[:-6], "%Y-%m-%d %H:%M:%S")
        return cls.expand_datetime(date, prefix)

    @classmethod
    def expand_datetime(self, date, prefix):
        # return dictionary with useful values
        return {
            prefix                  : date.strftime("%c"),
            prefix + '.year'        : unicode(date.year),
            prefix + '.month'       : unicode(date.month),
            prefix + '.day'         : unicode(date.day),
            prefix + '.hour'        : unicode(date.hour),
            prefix + '.hour12'      : date.strftime("%I"),
            prefix + '.ampm'        : date.strftime("%p"),
            prefix + '.minute'      : unicode(date.minute),
            prefix + '.second'      : unicode(date.second),
            prefix + '.weeknumber'  : date.strftime("%U"),
            prefix + '.monthshort'  : date.strftime("%b"),
            prefix + '.monthlong'   : date.strftime("%B"),
            prefix + '.dayshort'    : date.strftime("%a"),
            prefix + '.daylong'     : date.strftime("%A"),
            prefix + '.date'        : date.strftime("%x"),
            prefix + '.time'        : date.strftime("%X"),
        }

from    AppKit              import *
from    objc                import Category, lookUpClass
from    datetime            import datetime
from    quotefix.utils      import swizzle, Template
from    xml.sax.saxutils    import escape
import  re, email.utils

# enable personalized attribution by rigging the Message class
Message = lookUpClass('Message')
class Message(Category(Message)):

    @classmethod
    def __init__(cls, app):
        cls.app = app

    # replace Message (class-)methods with a version which inserts
    # a placeholder (to be replaced with a user-defined template in
    # render_attribution())
    @swizzle(Message, 'replyPrefixWithSpacer:')
    def replyPrefixWithSpacer(cls, original, arg):
        if cls.app.use_custom_reply_attribution:
            return "__CUSTOM_REPLY_ATTRIBUTION__"
        return original(cls, arg)

    @swizzle(Message, 'forwardedMessagePrefixWithSpacer:')
    def forwardedMessagePrefixWithSpacer(cls, original, arg):
        if cls.app.use_custom_forwarding_attribution:
            return "__CUSTOM_FORWARDING_ATTRIBUTION__"
        return original(cls, arg)

    # render a user-defined template to provide a customized attribution
    def render_attribution(self, text, inreplyto, forward):
        if forward:
            template    = self.app.custom_forwarding_attribution
            placeholder = "__CUSTOM_FORWARDING_ATTRIBUTION__"
        else:
            template    = self.app.custom_reply_attribution
            placeholder = "__CUSTOM_REPLY_ATTRIBUTION__"

        # setup template parameters
        params = {
            'message.from'          : inreplyto.sender(),
            'message.from.name'     : '',
            'message.from.email'    : '',
            'message.sender'        : inreplyto.sender(),
            'message.comment'       : inreplyto.senderAddressComment(),
            'message.to'            : inreplyto.to(),
            'message.subject'       : inreplyto.subject(),
            'response.from'         : self.sender(),
            'response.from.name'    : '',
            'response.from.email'   : '',
            'response.sender'       : self.sender(),
            'response.comment'      : self.senderAddressComment(),
            'response.to'           : self.to(),
            'response.subject'      : self.subject(),
        }
        params.update(self.expand_nsdate(inreplyto.dateSent(),        'message.sent'))
        params.update(self.expand_nsdate(inreplyto.dateReceived(),    'message.received'))
        params.update(self.expand_datetime(datetime.now(),            'now'))

        # try to split e-mail address from *.from
        for k in [ 'message.from', 'response.from' ]:
            try:    
                params[k + '.name'], params[k + '.email'] = email.utils.parseaddr(params[k])
            except:
                pass

        # expand template
        attribution = Template(template).substitute(params).encode('utf-8')

        # replace placeholder with new attribution
        return re.sub('^\s*' + placeholder, attribution, text)

    # expand an NSDate object to a dictionary
    def expand_nsdate(self, nsdate, prefix):
        # convert NSDate to datetime
        date = datetime.strptime(nsdate.description()[:-6], "%Y-%m-%d %H:%M:%S")
        return self.expand_datetime(date, prefix)

    def expand_datetime(self, date, prefix):
        # return dictionary with useful values
        return {
            prefix                  : date.strftime("%c"),
            prefix + '.year'        : date.year,
            prefix + '.month'       : date.month,
            prefix + '.day'         : date.day,
            prefix + '.hour'        : date.hour,
            prefix + '.hour12'      : date.strftime("%I"),
            prefix + '.ampm'        : date.strftime("%p"),
            prefix + '.minute'      : date.minute,
            prefix + '.second'      : date.second,
            prefix + '.weeknumber'  : date.strftime("%U"),
            prefix + '.monthshort'  : date.strftime("%b"),
            prefix + '.monthlong'   : date.strftime("%B"),
            prefix + '.dayshort'    : date.strftime("%a"),
            prefix + '.daylong'     : date.strftime("%A"),
            prefix + '.date'        : date.strftime("%x"),
            prefix + '.time'        : date.strftime("%X"),
        }

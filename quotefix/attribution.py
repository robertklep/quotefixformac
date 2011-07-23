from    AppKit              import *
from    objc                import Category, lookUpClass
from    datetime            import datetime
from    quotefix.utils      import swizzle, Template
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
        s = original(cls, arg)

        # rewrite original attribution string to a regular expression
        cls.original_reply_attribution = re.sub(r'%\d+\$\@', '.*?', s).strip()

        # return original
        return s

    @swizzle(Message, 'forwardedMessagePrefixWithSpacer:')
    def forwardedMessagePrefixWithSpacer(cls, original, arg):
        s = original(cls, arg)

        # rewrite original attribution string to a regular expression
        cls.original_forwarding_attribution = re.sub(r'%\d+\$\@', '.*?', s).strip()

        # return original
        return s

    # render a user-defined template to provide a customized attribution
    def render_attribution(self, inreplyto, is_forward):
        if is_forward:
            template = self.app.custom_forwarding_attribution
        else:
            template = self.app.custom_reply_attribution

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

        # add dates
        params.update(self.expand_nsdate(inreplyto.dateSent(),        'message.sent'))
        params.update(self.expand_nsdate(inreplyto.dateReceived(),    'message.received'))
        params.update(self.expand_datetime(datetime.now(),            'now'))

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
    def expand_nsdate(self, nsdate, prefix):
        # convert NSDate to datetime
        date = datetime.strptime(nsdate.description()[:-6], "%Y-%m-%d %H:%M:%S")
        return self.expand_datetime(date, prefix)

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

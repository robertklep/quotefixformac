from    AppKit          import *
from    objc            import Category, lookUpClass
from    datetime        import datetime
from    quotefix.utils  import swizzle, Template
import  re

# enable personalized attribution by rigging the Message class
oldMessage = lookUpClass('Message')
class Message(Category(oldMessage)):

    @classmethod
    def __init__(cls, app):
        cls.app = app

    @swizzle(oldMessage, 'replyPrefixWithSpacer:')
    def replyPrefixWithSpacer(cls, original, arg):
        if cls.app.use_custom_reply_attribution:
            return "__CUSTOM_REPLY_ATTRIBUTION__"
        return original(cls, arg)

    @swizzle(oldMessage, 'forwardedMessagePrefixWithSpacer:')
    def forwardedMessagePrefixWithSpacer(cls, original, arg):
        if cls.app.use_custom_forwarding_attribution:
            return "__CUSTOM_FORWARDING_ATTRIBUTION__"
        return original(cls, arg)

    def render_attribution(self, html, inreplyto, forward):
        if forward:
            template    = self.app.custom_forwarding_attribution
            placeholder = "__CUSTOM_FORWARDING_ATTRIBUTION__"
        else:
            template    = self.app.custom_reply_attribution
            placeholder = "__CUSTOM_REPLY_ATTRIBUTION__"

        # setup template parameters
        params = {
            'message.sender'    : inreplyto.sender(),
            'message.comment'   : inreplyto.senderAddressComment(),
            'message.to'        : inreplyto.to(),
            'message.subject'   : inreplyto.subject(),
            'response.sender'   : self.sender(),
            'response.comment'  : self.senderAddressComment(),
            'response.to'       : self.to(),
            'response.subject'  : self.subject(),
        }
        params.update(self.expand_nsdate(inreplyto.dateSent(),        'message.sent'))
        params.update(self.expand_nsdate(inreplyto.dateReceived(),    'message.received'))
        params.update(self.expand_nsdate(inreplyto.dateReceived(),    'message.lastviewed'))
        params.update(self.expand_nsdate(self.dateSent(),             'response.sent'))
        params.update(self.expand_nsdate(self.dateReceived(),         'response.received'))
        params.update(self.expand_nsdate(self.dateReceived(),         'response.lastviewed'))

        # expand template
        attribution = Template(template).substitute(params).encode('utf-8')

        # replace placeholder with new attribution
        return re.sub('^\s*' + placeholder, attribution, html)

    # expand an NSDate object to a dictionary
    def expand_nsdate(self, nsdate, prefix):
        # convert NSDate to datetime
        date = datetime.strptime(nsdate.description()[:-6], "%Y-%m-%d %H:%M:%S")

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

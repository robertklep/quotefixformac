from    AppKit      import *
from    Foundation  import *
from    datetime    import datetime
import  email.utils

class QFMessage:
    """ wraps a message """

    def __init__(self, message):
        self.From       = QFEmailAddress(message.sender())
        self.sender     = message.sender()
        self.comment    = message.senderAddressComment()
        self.to         = self.expand_nsarray( message.to() )
        try:
            self.cc     = self.expand_nsarray( message.ccRecipients() )
        except:
            self.cc     = ""
        self.subject    = message.subject()
        self.sent       = QFDateTime(message.dateSent())
        self.received   = QFDateTime(message.dateReceived())

    def expand_nsarray(self, obj, separator = ", "):
        if isinstance(obj, NSArray):
            return obj.componentsJoinedByString_(separator)
        return obj

class QFEmailAddress:
    """ wrap an e-mail address """

    def __init__(self, address):
        name, emailaddr = email.utils.parseaddr(address)
        self.email      = emailaddr
        self.name       = name or emailaddr

class QFDateTime(str):
    """ wraps a datetime object """

    def __new__(cls, dt):
        if isinstance(dt, NSDate):
            dt = cls.nsdate_to_datetime(dt)
        self            = super(QFDateTime, cls).__new__(cls, dt.strftime("%a %b %d %Y %H:%M:%S"))
        self.datetime   = dt
        self.year	    = dt.strftime("%Y")
        self.month	    = dt.strftime("%m")
        self.day	    = dt.strftime("%d")
        self.hour	    = dt.strftime("%H")
        self.hour12	    = dt.strftime("%I")
        self.ampm	    = dt.strftime("%p")
        self.minute	    = dt.strftime("%M")
        self.second	    = dt.strftime("%S")
        self.weeknumber = dt.strftime("%U")
        self.monthshort = dt.strftime("%b")
        self.monthlong  = dt.strftime("%B")
        self.dayshort   = dt.strftime("%a")
        self.daylong	= dt.strftime("%A")
        self.date	    = dt.strftime("%x")
        self.time	    = dt.strftime("%X")
        return self

    def strftime(self, fmt):
        return self.datetime.strftime(fmt)

    @classmethod
    def nsdate_to_datetime(cls, nsdate):
        # convert NSDate to datetime (XXX: always converts to local timezone)
        description = nsdate.descriptionWithCalendarFormat_timeZone_locale_("%Y-%m-%d %H:%M:%S", None, None)
        return datetime.strptime(description, "%Y-%m-%d %H:%M:%S")

from    AppKit      import *
from    Foundation  import *
from    datetime    import datetime
import  email.utils

class QFMessage:
    """ wraps a message """

    def __init__(self, message):
        self.From           = QFAddressee(message.sender())
        self.sender         = message.sender()
        self.comment        = message.senderAddressComment()
        self.to             = QFAddresseeList( message.to() )
        self.recipients     = QFRecipients(
            All     = message.recipients(),
            to      = message.toRecipients(),
            cc      = message.ccRecipients(),
            bcc     = message.bccRecipients(),
        )
        self.subject        = message.subject()
        self.sent           = QFDateTime(message.dateSent())
        self.received       = QFDateTime(message.dateReceived())

class QFRecipients:

    def __init__(self, All, to, cc, bcc):
        self.All    = QFAddresseeList(All)
        self.to     = QFAddresseeList(to)
        self.cc     = QFAddresseeList(cc)
        self.bcc    = QFAddresseeList(bcc)

    def __unicode__(self):
        return unicode(self.All)

class QFAddresseeList:

    def __init__(self, addresseelist):
        # convert to list if passed parameter is a string
        if isinstance(addresseelist, basestring):
            addresseelist = [ addresseelist ]

        # make a list of QFAddressee's
        self.addressees = []
        for addressee in list(addresseelist):
            # expand MessageAddressee instances
            if isinstance(addressee, MessageAddressee):
                addressee = "%s <%s>" % (addressee.displayName(), addressee.address())
            self.addressees.append( QFAddressee(addressee) )

    def join(self, separator = ", ", field = 'address'):
        if field not in [ 'address', 'name', 'email' ]:
            field = 'address'
        return separator.join([ unicode(getattr(a, field)) for a in self.addressees ])

    def __unicode__(self):
        return self.join(", ")

class QFAddressee:
    """ wrap a message addressee """

    def __init__(self, address):
        self.address        = address
        name, emailaddr     = email.utils.parseaddr(address)
        self.email          = emailaddr
        self.name           = name or emailaddr

    def __unicode__(self):
        return self.address

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

from    AppKit      import *
from    Foundation  import *
from    datetime    import datetime
import  email.utils, re

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

    def __len__(self):
        return len(self.All)

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

    def __len__(self):
        return len(self.addressees)

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
    formatter           = NSDateFormatter.alloc().init()
    STRFTIME_TO_UNICODE = {
        '%Y'    : 'YYYY',
        '%m'    : 'MM',
        '%d'    : 'dd',
        '%H'    : 'HH',
        '%I'    : 'hh',
        '%p'    : 'a',
        '%M'    : 'mm',
        '%S'    : 'ss',
        '%U'    : 'w',
        '%b'    : 'MMM',
        '%B'    : 'MMMM',
        '%a'    : 'E',
        '%A'    : 'EEEE',
        '%x'    : 'EEE MMM dd yyyy',
        '%X'    : 'HH:mm:ss',
        '%z'    : 'Z',
    }

    def __new__(cls, nsdate):
        cls.formatter.setDateFormat_("EEE MMM dd yyyy HH:mm:ss")
        self            = super(QFDateTime, cls).__new__(
            cls,
            cls.formatter.stringFromDate_(nsdate).encode('utf-8')
        )
        self.nsdate     = nsdate

        # set date/time attributes
        attributes      = dict(
            year        = "YYYY",
            month       = "MM",
            day         = "dd",
            hour        = "HH",
            hour12      = "hh",
            ampm        = "a",
            minute      = "mm",
            second      = "ss",
            weeknumber  = "w",
            monthshort  = "MMM",
            monthlong   = "MMMM",
            dayshort    = "E",
            daylong     = "EEEE",
            date        = "EEE MMM dd yyyy",
            time        = "HH:mm:ss",
            timezone    = "Z",
        )

        for attribute, format in attributes.items():
            self.formatter.setDateFormat_(format)
            setattr(self, attribute, self.formatter.stringFromDate_(nsdate).encode('utf-8'))

        return self

    def strftime_to_unicode(self, fmt):
        """ convert strftime formatting character to Unicode formatting string """
        return re.sub(
            r'(%[a-zA-Z])',
            lambda m: self.STRFTIME_TO_UNICODE.get(m.group(1), m.group(1)),
            fmt
        )

    def strftime(self, fmt, locale = None):
        return self.format(self.strftime_to_unicode(fmt), locale)

    def format(self, fmt, locale = None):
        self.formatter.setDateFormat_(fmt)
        if locale:
            self.formatter.setLocale_(NSLocale.alloc().initWithLocaleIdentifier_(locale))
        return self.formatter.stringFromDate_(self.nsdate).encode('utf-8')

    def locale(self, locale):
        return self.format("EEE MMM dd yyyy HH:mm:ss", locale)

    @classmethod
    def nsdate_to_datetime(cls, nsdate):
        # convert NSDate to datetime (XXX: always converts to local timezone)
        description = nsdate.descriptionWithCalendarFormat_timeZone_locale_("%Y-%m-%d %H:%M:%S", None, None)
        return datetime.strptime(description, "%Y-%m-%d %H:%M:%S")

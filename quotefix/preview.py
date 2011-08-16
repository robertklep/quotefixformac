from    quotefix.attributionclasses import QFMessage
from    datetime                    import datetime, timedelta

class PreviewMessage:

    sender                  = lambda s: "Original Sender <original@sender.domain>"
    senderAddressComment    = lambda s: "Original Sender"
    to                      = lambda s: "Original Receiver <original@sender.domain>"
    subject                 = lambda s: "This is the original subject"
    dateSent                = lambda s: datetime.now() - timedelta(seconds = 3600)
    dateReceived            = lambda s: datetime.now() - timedelta(seconds = 1800)
    toRecipients            = lambda s: [ "Original Receiver <original@sender.dom>" ]
    ccRecipients            = lambda s: [ "CC Recip 1 <cc1@test>", "CC Recip 2 <cc2@test>" ]
    recipients              = lambda s: s.toRecipients() + s.ccRecipients()
    bccRecipients           = lambda s: []

class PreviewResponse:

    sender                  = lambda s: "Your Name <you@some.domain>"
    senderAddressComment    = lambda s: "Your Name"
    to                      = lambda s: "New Receiver <new@receiver.domain>"
    subject                 = lambda s: "This is the *new* subject"
    dateSent                = lambda s: datetime.now()
    dateReceived            = lambda s: datetime.now()
    recipients              = lambda s: []
    toRecipients            = lambda s: []
    ccRecipients            = lambda s: []
    bccRecipients           = lambda s: []

# 'fake' message to preview custom reply/forward attribution
preview_message = {
    'message'   : QFMessage(PreviewMessage()),
    'response'  : QFMessage(PreviewResponse())
}

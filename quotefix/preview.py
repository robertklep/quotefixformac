from    quotefix.attributionclasses import QFMessage
from    datetime                    import datetime, timedelta

class PreviewMessage:

    sender                  = lambda s: "Original Sender <original@sender.domain>"
    senderAddressComment    = lambda s: "Original Sender"
    to                      = lambda s: "Original Receiver <original@sender.domain>"
    subject                 = lambda s: "This is the original subject"
    dateSent                = lambda s: datetime.now() - timedelta(seconds = 3600)
    dateReceived            = lambda s: datetime.now() - timedelta(seconds = 1800)

class PreviewResponse:

    sender                  = lambda s: "Your Name <you@some.domain>"
    senderAddressComment    = lambda s: "Your Name"
    to                      = lambda s: "New Receiver <new@receiver.domain>"
    subject                 = lambda s: "This is the *new* subject"
    dateSent                = lambda s: datetime.now()
    dateReceived            = lambda s: datetime.now()

# 'fake' message to preview custom reply/forward attribution
preview_message = {
#    'message'   : QFMessage(PreviewMessage()),
#    'response'  : QFMessage(PreviewResponse())
}

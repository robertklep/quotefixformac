from    AppKit          import *
from    Foundation      import *
from    quotefix        import *
import  objc

class QuoteFix(objc.runtime.MVMailBundle):

    @classmethod
    def initialize(cls):
        # instantiate updater
        updater = Updater()

        # register ourselves
        objc.runtime.MVMailBundle.registerBundle()

        # extract plugin version from Info.plist
        bundle  = NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix')
        version = bundle.infoDictionary().get('CFBundleVersion', '??')

        # initialize app
        app = App(version, updater)

        # initialize our posing classes with app instance
        MailDocumentEditor.registerQuoteFixApplication(app)
        MessageHeaders.registerQuoteFixApplication(app)
        MailApp.registerQuoteFixApplication(app)
        QuoteFixPreferencesController.registerQuoteFixApplication(app)
        CustomizedAttribution.registerQuoteFixApplication(app)

        # announce that we have loaded
        NSLog("QuoteFix Plugin (version %s) registered with Mail.app" % version)

from    AppKit          import *
from    Foundation      import *
from    quotefix        import *
import  objc

MVMailBundle = objc.lookUpClass('MVMailBundle')

class QuoteFix(MVMailBundle):

    @classmethod
    def initialize(cls):
        # load updater class (early)
        updater = Updater()

        # register ourselves
        MVMailBundle.registerBundle()

        # extract plugin version from Info.plist
        bundle  = NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix')
        version = bundle.infoDictionary().get('CFBundleVersion', '??')

        # initialize app
        app = App(version)

        # initialize our posing classes with app instance
        MailDocumentEditor.__init__(app)
        QuoteFixPreferencesController.__init__(app)
        Message.__init__(app)

        # initialize updater
        updater.set_app(app)

        # announce that we have loaded
        NSLog("QuoteFix Plugin (version %s) registered with Mail.app" % version)

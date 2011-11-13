import  sys, os.path

path    = os.path.dirname(__file__)
libdir  = "lib/python" + sys.version[:3]
sys.path.insert(0, os.path.join(path, libdir))

from    AppKit          import *
from    Foundation      import *
from    quotefix        import *
from    quotefix.utils  import swizzle
import  objc, sys

if False:
    import threading, time, os
    class Watcher(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.watchmodules = []
            for module in sys.modules.keys():
                if not module.startswith('quotefix'):
                    continue
                module = sys.modules[module]
                if not module:
                    continue
                mtime = os.stat(module.__file__.replace('.pyc', '.py')).st_mtime
                self.watchmodules.append( (module, mtime) )

        def run(self):
            while True:
                for i, (module, mtime) in enumerate(self.watchmodules):
                    newmtime = os.stat(module.__file__.replace('.pyc', '.py')).st_mtime
                    if newmtime > mtime:
                        NSLog("reloading %s" % module.__name__)
                        reload(module)
                        self.watchmodules[i] = (module, newmtime)
                time.sleep(3)

    Watcher().start()

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
        QuoteFixPreferencesController.registerQuoteFixApplication(app)
        CustomizedAttribution.registerQuoteFixApplication(app)

        # announce that we have loaded
        NSLog("QuoteFix Plugin (version %s) registered with Mail.app" % version)

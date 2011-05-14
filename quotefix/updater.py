from    AppKit      import *
from    Foundation  import *
import  objc, os, os.path

class Updater:

    def __init__(self, app = None):
        bundle         = NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix')
        frameworkspath = bundle.privateFrameworksPath()
        sparklepath    = os.path.join(frameworkspath, 'Sparkle.framework')
        objc.loadBundle('Sparkle', globals(), bundle_path = sparklepath)
        self.updater   = SUUpdater.updaterForBundle_(bundle)
        self.app       = app

    def set_app(self, app):
        self.app = app

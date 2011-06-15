from    AppKit          import *
from    Foundation      import *
from    datetime        import datetime
from    quotefix.alert  import Alert
import  objc, os, os.path, logging

# load Sparkle framework
BUNDLE          = NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix')
frameworkspath  = BUNDLE.privateFrameworksPath()
sparklepath     = os.path.join(frameworkspath, 'Sparkle.framework')
sparkle         = dict() # use 'private' storage to keep Sparkle classes in
objc.loadBundle('Sparkle', sparkle, bundle_path = sparklepath)

class Updater:

    def __init__(self):
        # instantiate Sparkle updater
        try:
            self.updater = sparkle['SUUpdater'].updaterForBundle_(BUNDLE)
        except:
            NSLog("QuoteFix: updater error - cannot initialize the updater for QuoteFix. This usually happens because of compatibility issues between Mail plugins. Updates are disabled, but QuoteFix should function normally.")
            self.enabled = False
            return

        # set delegate
        self.updater.setDelegate_(UpdaterDelegate.alloc().init().retain())

        # reset update cycle
        self.updater.resetUpdateCycle()

        # updates are enabled
        self.enabled = True

    # check for updates now
    def check_for_updates(self):
        if not self.enabled:
            return
        logging.debug("checking for updates (URL = %s)" % self.updater.feedURL())
        self.updater.checkForUpdatesInBackground()

    @property
    def last_update_check(self):
        if not self.enabled:
            return None
        nsdate = self.updater.lastUpdateCheckDate()
        if nsdate:
            return datetime.strptime(nsdate.description()[:-6], "%Y-%m-%d %H:%M:%S")
        return None

    @property
    def check_update_interval(self):
        if not self.enabled:
            return None
        return self.updateCheckInterval()

    @check_update_interval.setter
    def check_update_interval(self, interval):
        if not self.enabled:
            return
        # only update when value changes (because changing it triggers
        # a reset of the update cycle)
        if self.check_update_interval == interval:
            return
        self.setAutomaticallyChecksForUpdates_(interval and True or False)
        self.setUpdateCheckInterval_(interval);

class UpdaterDelegate(NSObject):

    # relaunch Mail instead of the plugin
    def pathToRelaunchForUpdater_(self, updater):
        return NSBundle.mainBundle().bundlePath()

    def updater_didFinishLoadingAppcast_(self, updater, appcast):
        logging.debug("Updater finished loading appcast.")

    def updaterDidNotFindUpdate_(self, updater):
        logging.debug("Updater did not find update.")

    def updater_didFindValidUpdate_(self, updater, update):
        logging.debug("Updater found valid update.")

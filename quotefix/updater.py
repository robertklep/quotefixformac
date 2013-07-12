from    AppKit          import *
from    Foundation      import *
from    datetime        import datetime
from    logger          import logger
import  objc, os, os.path

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
        logger.debug("checking for updates (URL = %s)" % self.updater.feedURL())
        self.updater.checkForUpdatesInBackground()

    @property
    def last_update_check(self):
        if not self.enabled:
            return None
        return self.updater.lastUpdateCheckDate()

    def set_update_interval(self, interval):
        if not self.enabled:
            return

        # disable check if interval == 0
        if interval == 0:
            self.updater.setAutomaticallyChecksForUpdates_(False)
            return

        # only update when value changes (because changing it triggers
        # a reset of the update cycle)
        if self.updater.updateCheckInterval() == interval:
            return
        self.updater.setAutomaticallyChecksForUpdates_(True)
        self.updater.setUpdateCheckInterval_(interval);

class UpdaterDelegate(NSObject):

    # relaunch Mail instead of the plugin
    def pathToRelaunchForUpdater_(self, updater):
        return NSBundle.mainBundle().bundlePath()

    def updater_didFinishLoadingAppcast_(self, updater, appcast):
        logger.debug("Updater finished loading appcast.")

    def updaterDidNotFindUpdate_(self, updater):
        logger.debug("Updater did not find update.")

    def updater_didFindValidUpdate_(self, updater, update):
        logger.debug("Updater found valid update.")

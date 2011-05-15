from    AppKit      import *
from    Foundation  import *
from    datetime    import datetime
import  objc, os, os.path

# load Sparkle framework
BUNDLE         = NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix')
frameworkspath = BUNDLE.privateFrameworksPath()
sparklepath    = os.path.join(frameworkspath, 'Sparkle.framework')
objc.loadBundle('Sparkle', globals(), bundle_path = sparklepath)

class Updater:

    def __init__(self):
        # instantiate Sparkle updater
        self.updater = SUUpdater.updaterForBundle_(BUNDLE)

        # set delegate
        self.updater.setDelegate_(UpdaterDelegate.alloc().init().retain())

        # reset update cycle
        self.updater.resetUpdateCycle()

    # check for updates now
    def check_for_updates(self):
        self.updater.checkForUpdatesInBackground()

    @property
    def last_update_check(self):
        nsdate = self.updater.lastUpdateCheckDate()
        if nsdate:
            return datetime.strptime(nsdate.description()[:-6], "%Y-%m-%d %H:%M:%S")
        return None

    @property
    def check_update_interval(self):
        return self.updateCheckInterval()

    @check_update_interval.setter
    def check_update_interval(self, interval):
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

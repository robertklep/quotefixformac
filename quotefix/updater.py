from    AppKit          import *
from    Foundation      import *
from    datetime        import datetime
import  objc, os, os.path, logging, atexit

class Updater:

    def __init__(self):
        self.start_updater_app()

    def start_updater_app(self):
        self.enabled  = False
        return

        # clean environment
        if 'PYOBJC_BUNDLE_ADDRESS' in os.environ:
            os.environ.pop('PYOBJC_BUNDLE_ADDRESS')

        # find and start updater
        bundle  = NSBundle.bundleWithIdentifier_("name.klep.mail.QuoteFix")
        app     = NSWorkspace.sharedWorkspace().launchApplicationAtURL_options_configuration_error_(
            bundle.URLForResource_withExtension_("QuoteFixUpdater", "app"),
            NSWorkspaceLaunchWithoutAddingToRecents | NSWorkspaceLaunchAsync,
            {},
            None
        )
        self._updater = None
        self.enabled  = True

    @property
    def updater(self):
        # don't bother if we're not enabled
        if not self.enabled:
            return None

        # seem to have a valid connection to the updater
        if self._updater:
            # check if connection is still valid before we return it
            if self._updater.connectionForProxy().isValid():
                return self._updater
            # try to start updater app again
            self.start_updater_app()

        # try to connect to updater process
        failcount = 0
        while not self._updater:
            # create connection with quotefix updater process
            self._updater = NSConnection.rootProxyForConnectionWithRegisteredName_host_(
                "QuoteFixUpdater",
                None
            )
            if self._updater:
                # initialize updater
                self._updater.initializeForBundle_relaunchPath_(
                    NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix'),
                    NSBundle.mainBundle().executablePath()
                )
                self.enabled = True
                break

            # keep track of fails
            failcount += 1
            if failcount > 10:
                NSLog("Couldn't contact updater after 10 seconds!")
                self.enabled = False
                return None

            # sleep a second and try again
            NSRunLoop.currentRunLoop().runMode_beforeDate_(
                NSDefaultRunLoopMode,
                NSDate.date().dateByAddingTimeInterval_(1)
            )
        return self._updater

    # check for updates now
    def check_for_updates(self):
        if not self.enabled:
            return
        self.updater.checkForUpdatesInBackground()

    @property
    def last_update_check(self):
        if not self.enabled:
            return None
        return self.updater.lastUpdateCheckDate()

    @property
    def check_update_interval(self):
        if not self.enabled:
            return None
        return self.updater.updateCheckInterval()

    @check_update_interval.setter
    def check_update_interval(self, interval):
        if not self.enabled:
            return
        # only update when value changes (because changing it triggers
        # a reset of the update cycle)
        if self.check_update_interval == interval:
            return
        self.updater.setAutomaticallyChecksForUpdates_(interval and True or False)
        self.updater.setUpdateCheckInterval_(interval);

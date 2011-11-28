from    AppKit          import *
from    Foundation      import *
from    datetime        import datetime
import  objc, os, os.path, logging, atexit

class Updater:

    def __init__(self):
        self.start_updater_app()

    def start_updater_app(self):
        NSLog("QuoteFix plug-in starting updater process")
        # find and start updater
        bundle  = NSBundle.bundleWithIdentifier_("name.klep.mail.QuoteFix")
        app     = NSWorkspace.sharedWorkspace().launchApplicationAtURL_options_configuration_error_(
            bundle.URLForResource_withExtension_("QuoteFixUpdater", "app"),
            0, # NSWorkspaceLaunchWithoutAddingToRecents | NSWorkspaceLaunchAsync,
            {},
            None
        )
        self._updater       = None
        self.updater_failed = False
        self.enabled        = True

    @property
    def updater(self):
        # don't bother if we're not enabled
        if not self.enabled:
            return None

        # seem to have a connection to the updater
        if self._updater and not self.updater_failed:
            # check if connection is still valid before we return it
            if self._updater.connectionForProxy().isValid():
                return self._updater
            self.updater_failed = True

        # try to start updater app again
        if self.updater_failed:
            self.start_updater_app()
            self.updater_failed = False

        # try to connect to updater process
        failcount = 0
        while not self._updater:
            # create connection with quotefix updater process
            self._updater = NSConnection.rootProxyForConnectionWithRegisteredName_host_(
                "QuoteFixUpdater",
                None
            )
            if self._updater:
                # set timeouts
                connection = self._updater.connectionForProxy()
                connection.setRequestTimeout_(3)
                connection.setReplyTimeout_(3)
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
                NSDate.dateWithTimeIntervalSinceNow_(1)
            )
        return self._updater

    # check for updates now
    def check_for_updates(self):
        if not self.enabled:
            return
        try:
            self.updater.checkForUpdatesInBackground()
        except:
            self.updater_failed = True

    @property
    def last_update_check(self):
        if not self.enabled:
            NSLog("last update check: not enabled")
            return None
        try:
            return self.updater.lastUpdateCheckDate()
        except:
            NSLog("last update check: failed")
            self.updater_failed = True
            return None

    @property
    def check_update_interval(self):
        if not self.enabled:
            return None
        try:
            return self.updater.updateCheckInterval()
        except:
            self.updater_failed = True
            return None

    @check_update_interval.setter
    def check_update_interval(self, interval):
        if not self.enabled:
            return
        # only update when value changes (because changing it triggers
        # a reset of the update cycle)
        if self.check_update_interval == interval:
            return
        try:
            self.updater.setAutomaticallyChecksForUpdates_(interval and True or False)
            self.updater.setUpdateCheckInterval_(interval);
        except:
            self.updater_failed = True

from    AppKit          import *
from    Foundation      import *
from    datetime        import datetime
import  objc, os, os.path, logging, atexit

class Updater:

    def __init__(self):
        # find and start updater
        bundle  = NSBundle.bundleWithIdentifier_("name.klep.mail.QuoteFix")
        app     = NSWorkspace.sharedWorkspace().launchApplicationAtURL_options_configuration_error_(
            bundle.URLForResource_withExtension_("QuoteFixUpdater", "app"),
            0,
            {},
            None
        )
        self._updater = None
        self.enabled  = True

    @property
    def updater(self):
        if not self.enabled:
            return None
        if self._updater:
            return self._updater
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

    def __dealloc__(self):
        NSLog("dealloc: cleaning up")
        if self.enabled:
            self.updater.quit()

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

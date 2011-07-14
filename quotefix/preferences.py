from    AppKit          import *
from    Foundation      import *
from    quotefix.alert  import Alert
import  objc

# controller for NIB controls
class QuoteFixPreferencesController(NSObject):
    removeQuotes                    = objc.IBOutlet()
    removeQuotesLevel               = objc.IBOutlet()
    keepAttributionWhitespace       = objc.IBOutlet()
    removeTrailingWhitespace        = objc.IBOutlet()
    useCustomReplyAttribution       = objc.IBOutlet()
    customReplyAttribution          = objc.IBOutlet()
    useCustomForwardingAttribution  = objc.IBOutlet()
    customForwardingAttribution     = objc.IBOutlet()
    updateInterval                  = objc.IBOutlet()
    lastUpdateCheck                 = objc.IBOutlet()
    currentVersion                  = objc.IBOutlet()
    checkUpdateButton               = objc.IBOutlet()
    debugging                       = objc.IBOutlet()
    helpButton                      = objc.IBOutlet()
    _window                         = objc.IBOutlet()

    @classmethod
    def __init__(cls, app):
        cls.app = app

    def set_remove_quotes_level(self):
        value = self.removeQuotesLevel.intValue()
        if value < 1:
            Alert.showAlert(self, "Invalid level", "Please enter a level of 1 or higher.")
            return
        self.removeQuotes.setState_(1)
        self.app.remove_quotes          = True
        self.app.remove_quotes_level    = value

    @objc.IBAction
    def changeRemoveQuotes_(self, sender):
        if sender.state():  # enable
            self.set_remove_quotes_level()
        else:               # disable
            self.app.remove_quotes = False

    @objc.IBAction
    def changeRemoveQuotesLevel_(self, sender):
        self.set_remove_quotes_level()

    @objc.IBAction
    def changeRemoveTrailingWhitespace_(self, sender):
        self.app.remove_trailing_whitespace = sender.state()

    @objc.IBAction
    def changeKeepAttributionWhitespace_(self, sender):
        self.app.keep_attribution_whitespace = sender.state()

    @objc.IBAction
    def changeUseCustomReplyAttribution_(self, sender):
        self.app.use_custom_reply_attribution = sender.state()

    @objc.IBAction
    def changeCustomReplyAttribution_(self, sender):
        self.app.custom_reply_attribution = sender.stringValue()

    @objc.IBAction
    def changeUseCustomForwardingAttribution_(self, sender):
        self.app.use_custom_forwarding_attribution = sender.state()

    @objc.IBAction
    def changeCustomForwardingAttribution_(self, sender):
        self.app.custom_forwarding_attribution = sender.stringValue()

    @objc.IBAction
    def changeUpdateInterval_(self, sender):
        self.app.check_update_interval = sender.selectedSegment()

    @objc.IBAction
    def performUpdateCheckNow_(self, sender):
        self.app.check_for_updates()
        self.setLastUpdateCheck()

    @objc.IBAction
    def changeDebugging_(self, sender):
        self.app.is_debugging = sender.state()

    @objc.IBAction
    def helpButtonPressed_(self, sender):
        # open help url
        NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_("http://code.google.com/p/quotefixformac/wiki/CustomAttribution"))

    def awakeFromNib(self):
        self.currentVersion.setStringValue_(self.app.version)
        self.keepAttributionWhitespace.setState_(self.app.keep_attribution_whitespace)
        self.removeTrailingWhitespace.setState_(self.app.remove_trailing_whitespace)
        self.debugging.setState_(self.app.is_debugging)
        self.removeQuotes.setState_(self.app.remove_quotes)
        self.removeQuotesLevel.setIntValue_(self.app.remove_quotes_level)
        self.useCustomReplyAttribution.setState_(self.app.use_custom_reply_attribution)
        self.customReplyAttribution.setStringValue_(self.app.custom_reply_attribution)
        self.useCustomForwardingAttribution.setState_(self.app.use_custom_forwarding_attribution)
        self.customForwardingAttribution.setStringValue_(self.app.custom_forwarding_attribution)
        self.updateInterval.setSelectedSegment_(self.app.check_update_interval)
        self.setLastUpdateCheck()

    def setLastUpdateCheck(self):
        date = self.app.last_update_check
        self.lastUpdateCheck.setStringValue_(date and date.strftime("%c") or "Never")

    def window(self):
        """ Called by Alert() """
        return self._window

    # act as a delegate for text fields
    def controlTextDidChange_(self, notification):
        obj = notification.object()
        if obj == self.customReplyAttribution:
            self.changeCustomReplyAttribution_(obj)
        elif obj == self.customForwardingAttribution:
            self.changeCustomForwardingAttribution_(obj)

    def control_textView_doCommandBySelector_(self, control, textview, selector):
        if str(selector) == 'insertNewline:':
            textview.insertNewlineIgnoringFieldEditor_(self)
            return True
        return False

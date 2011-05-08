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
    def changeDebugging_(self, sender):
        self.app.is_debugging = sender.state()

    @objc.IBAction
    def helpButtonPressed_(self, sender):
        # open help url
        NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_("http://code.google.com/p/quotefixformac/wiki/CustomAttribution"))

    def awakeFromNib(self):
        self.keepAttributionWhitespace.setState_(self.app.keep_attribution_whitespace)
        self.removeTrailingWhitespace.setState_(self.app.remove_trailing_whitespace)
        self.debugging.setState_(self.app.is_debugging)
        self.removeQuotes.setState_(self.app.remove_quotes)
        self.removeQuotesLevel.setIntValue_(self.app.remove_quotes_level)
        self.useCustomReplyAttribution.setState_(self.app.use_custom_reply_attribution)
        self.customReplyAttribution.setStringValue_(self.app.custom_reply_attribution)
        self.useCustomForwardingAttribution.setState_(self.app.use_custom_forwarding_attribution)
        self.customForwardingAttribution.setStringValue_(self.app.custom_forwarding_attribution)

    def window(self):
        """ Called by Alert() """
        return self._window

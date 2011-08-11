# -*- coding:utf-8 -*-
from    AppKit                  import *
from    Foundation              import *
from    quotefix.utils          import swizzle
from    quotefix.attribution    import CustomizedAttribution
from    quotefix.preview        import preview_message
from    datetime                import datetime, timedelta
import  objc, random

class QuoteFixPreferencesModule(NSPreferencesModule):

    def init(self):
        context     = { NSNibTopLevelObjects : [] }
        nib         = NSNib.alloc().initWithNibNamed_bundle_("QuoteFixPreferencesModule.nib", NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix'))
        inited      = nib.instantiateNibWithExternalNameTable_(context)
        self.view   = filter(lambda _: isinstance(_, NSBox), context[NSNibTopLevelObjects])[0]
        self.setMinSize_(self.view.boundsSize())
        self.setPreferencesView_(self.view)
        return self

    def minSize(self):
        return self.view.boundsSize()

    def isResizable(self):
        return False

class QuoteFixPreferences(NSPreferences):

    @classmethod
    def injectPreferencesModule(cls, prefs):
        titles = objc.getInstanceVariable(prefs, '_preferenceTitles')
        if 'QuoteFix' not in titles:
            prefs.addPreferenceNamed_owner_("QuoteFix", QuoteFixPreferencesModule.sharedInstance())
            toolbar     = objc.getInstanceVariable(prefs, '_preferencesPanel').toolbar()
            numitems    = len( toolbar.items() )
            toolbar.insertItemWithItemIdentifier_atIndex_("QuoteFix", numitems)

    @swizzle(NSPreferences, 'showPreferencesPanel')
    def showPreferencesPanel(self, original):
        QuoteFixPreferences.injectPreferencesModule(self)
        original(self)

# controller for NIB controls
class QuoteFixPreferencesController(NSObject):
    enableDisableButton             = objc.IBOutlet()
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

    @classmethod
    def registerQuoteFixApplication(cls, app):
        cls.app = app
        # inject preferences module
        prefs = NSPreferences.sharedPreferences()
        if prefs:
            QuoteFixPreferences.injectPreferencesModule(prefs)

    def set_remove_quotes_level(self):
        value = self.removeQuotesLevel.intValue()
        if value < 1:
            self.removeQuotesLevel.setIntValue_(self.app.remove_quotes_level)
            NSRunAlertPanel("Invalid level", "Please enter a level of 1 or higher.", None, None, None)
            return
        self.removeQuotes.setState_(1)
        self.app.remove_quotes          = True
        self.app.remove_quotes_level    = value

    @objc.IBAction
    def changeEnableDisable_(self, sender):
        if sender.state():  # enable
            self.app.is_active = True
        else:               # disable
            self.app.is_active = False
#        sender.setTitle_("QuoteFix is %s" % (self.app.is_active and "enabled" or "disabled"))

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
        self.set_preview(sender)

    @objc.IBAction
    def changeUseCustomForwardingAttribution_(self, sender):
        self.app.use_custom_forwarding_attribution = sender.state()

    @objc.IBAction
    def changeCustomForwardingAttribution_(self, sender):
        self.app.custom_forwarding_attribution = sender.stringValue()
        self.set_preview(sender)

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
        self.enableDisableButton.setState_(self.app.is_active)
        self.keepAttributionWhitespace.setState_(self.app.keep_attribution_whitespace)
        self.removeTrailingWhitespace.setState_(self.app.remove_trailing_whitespace)
        self.debugging.setState_(self.app.is_debugging)
        self.removeQuotes.setState_(self.app.remove_quotes)
        self.removeQuotesLevel.setIntValue_(self.app.remove_quotes_level)
        self.useCustomReplyAttribution.setState_(self.app.use_custom_reply_attribution)
        self.customReplyAttribution.setStringValue_(self.app.custom_reply_attribution)
        self.set_preview(self.customReplyAttribution)
        self.useCustomForwardingAttribution.setState_(self.app.use_custom_forwarding_attribution)
        self.customForwardingAttribution.setStringValue_(self.app.custom_forwarding_attribution)
        self.set_preview(self.customForwardingAttribution)
        self.updateInterval.setSelectedSegment_(self.app.check_update_interval)
        self.setLastUpdateCheck()

    def setLastUpdateCheck(self):
        date = self.app.last_update_check
        self.lastUpdateCheck.setStringValue_(date and date.strftime("%c") or "Never")

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

    def set_preview(self, sender):
        preview = CustomizedAttribution.render_with_params(
            sender.stringValue(),
            preview_message
        )
        # make newlines visible
        preview = preview.replace('\n', u'⤦\n')
        sender.setToolTip_(preview)

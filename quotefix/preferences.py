# -*- coding:utf-8 -*-
from    AppKit                  import *
from    Foundation              import *
from    quotefix.utils          import swizzle
from    quotefix.attribution    import CustomizedAttribution
from    quotefix.preview        import preview_message
from    datetime                import datetime, timedelta
import  objc, random, logging

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
    updateInterval                      = objc.IBOutlet()
    lastUpdateCheck                     = objc.IBOutlet()
    currentVersion                      = objc.IBOutlet()
    checkUpdateButton                   = objc.IBOutlet()
    helpButton                          = objc.IBOutlet()

    @classmethod
    def registerQuoteFixApplication(cls, app):
        cls.app = app
        # inject preferences module
        prefs = NSPreferences.sharedPreferences()
        if prefs:
            QuoteFixPreferences.injectPreferencesModule(prefs)

    @objc.IBAction
    def changeDebugging_(self, sender):
        is_debugging = sender.state()
        logging.getLogger('').setLevel(is_debugging and logging.DEBUG or logging.WARNING)
        if is_debugging:
            logging.debug('debug logging active')

    @objc.IBAction
    def changeUpdateInterval_(self, sender):
        self.app.check_update_interval = sender.selectedSegment()

    @objc.IBAction
    def performUpdateCheckNow_(self, sender):
        self.app.check_for_updates()
        self.setLastUpdateCheck()

    @objc.IBAction
    def helpButtonPressed_(self, sender):
        # open help url
        NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_("http://code.google.com/p/quotefixformac/wiki/CustomAttribution"))

    def awakeFromNib(self):
        self.currentVersion.setStringValue_(self.app.version)
        self.updateInterval.setSelectedSegment_(self.app.check_update_interval)
        self.setLastUpdateCheck()

    def setLastUpdateCheck(self):
        date = self.app.last_update_check
        self.lastUpdateCheck.setStringValue_(date and date.strftime("%c") or "Never")

    # act as a delegate for text fields
    def controlTextDidChange_(self, notification):
        obj = notification.object()
        tag = obj.tag()
        # update previews when customized attribution fields change
        if tag in [ 31, 32 ]:
            self.set_preview(obj)

    def control_textView_doCommandBySelector_(self, control, textview, selector):
        if str(selector) == 'insertNewline:':
            textview.insertNewlineIgnoringFieldEditor_(self)
            return True
        return False

    # render a preview message for customized attributions
    def set_preview(self, sender):
        return
        preview = CustomizedAttribution.render_with_params(
            sender.stringValue(),
            preview_message
        )
        # make newlines visible
        preview = preview.replace('\n', u'⤦\n')
        sender.setToolTip_(preview)

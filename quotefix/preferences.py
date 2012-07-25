# -*- coding:utf-8 -*-
from    AppKit                  import *
from    Foundation              import *
from    quotefix.utils          import swizzle, htmlunescape
from    quotefix.attribution    import CustomizedAttribution
from    quotefix.preview        import preview_message
from    datetime                import datetime, timedelta
import  objc, random, logging, re

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
    currentVersionUpdater               = objc.IBOutlet()
    checkUpdateButton                   = objc.IBOutlet()
    customReplyAttribution              = objc.IBOutlet()
    customForwardingAttribution         = objc.IBOutlet()
    customSignatureMatcher              = objc.IBOutlet()
    customSignatureMatcherFeedback      = objc.IBOutlet()
    customSignatureMatcherDefault       = objc.IBOutlet()
    helpButton                          = objc.IBOutlet()
    donateButton                        = objc.IBOutlet()
    cssFileBrowserButton	            = objc.IBOutlet()

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
    def donateButtonPressed_(self, sender):
        NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_("https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4UF2KB2BTW6AC"))

    @objc.IBAction
    def cssFileBrowserButtonPressed_(self, sender):
        openPanel = NSOpenPanel.openPanel()

        def openPanelDidClose_(result):
            if result == NSFileHandlingPanelOKButton:
                openPanel.orderOut_(self)
                self.app.custom_css_file = openPanel.filename()

        openPanel.beginSheetModalForWindow_completionHandler_(
            self.app.window(),
            objc.selector(openPanelDidClose_, argumentTypes='l')
        )

    @objc.IBAction
    def helpButtonPressed_(self, sender):
        # open help url
        NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_("http://code.google.com/p/quotefixformac/wiki/CustomAttribution"))

    def awakeFromNib(self):
        self.currentVersionUpdater.setStringValue_(self.app.version)
        self.updateInterval.setSelectedSegment_(self.app.check_update_interval)
        self.setLastUpdateCheck()

        # set donate image
        bundle  = NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix')
        path    = bundle.pathForResource_ofType_("donate", "gif")
        image   = NSImage.alloc().initByReferencingFile_(path)
        self.donateButton.setImage_(image)

        # check custom signature matcher
        self.check_signature_matcher(self.customSignatureMatcher)
        self.customSignatureMatcherDefault.setStringValue_(self.app.default_signature_matcher)

        # set attribution previews
        self.set_preview(self.customReplyAttribution)
        self.set_preview(self.customForwardingAttribution)

    def setLastUpdateCheck(self):
        date = self.app.last_update_check
        if date:
            formatter = NSDateFormatter.alloc().init()
            # use current user locale for 'last update' timestamp
            formatter.setLocale_(NSLocale.currentLocale())
            formatter.setDateFormat_("EEE MMM dd yyyy HH:mm:ss")
            date = formatter.stringFromDate_(date)
        self.lastUpdateCheck.setStringValue_(date)

    # act as a delegate for text fields
    def controlTextDidChange_(self, notification):
        obj = notification.object()
        tag = obj.tag()
        # update previews when customized attribution fields change
        if tag in [ 31, 32 ]:
            self.set_preview(obj)
        # check custom signature matcher and provide feedback
        elif tag in [ 50 ]:
            self.check_signature_matcher(obj)

    def control_textView_doCommandBySelector_(self, control, textview, selector):
        if str(selector) == 'insertNewline:':
            textview.insertNewlineIgnoringFieldEditor_(self)
            return True
        return False

    # check custom signature for a valid regular expression
    def check_signature_matcher(self, obj):
        regex       = obj.stringValue()
        feedback    = self.customSignatureMatcherFeedback
        try:
            re.compile(regex)
            feedback.setColor_(NSColor.greenColor())
            feedback.setToolTip_("")
        except re.error, e:
            feedback.setColor_(NSColor.redColor())
            feedback.setToolTip_(str(e))

    # render a preview message for customized attributions
    def set_preview(self, sender):
        viewers = MessageViewer.allMessageViewers()
        if not viewers:
            return
        messages = viewers[0].selectedMessages()
        if not messages:
            return

        preview = CustomizedAttribution.render_attribution(
            messages[0],
            messages[0],
            sender.stringValue(),
            False
        )

        # make newlines visible
        preview = preview.replace('\n', u'⤦\n')
        sender.setToolTip_(htmlunescape(preview))

from    AppKit          import *
from    Foundation      import *
from    quotefix.menu   import Menu
from    quotefix.alert  import Alert
from    objc            import Category, lookUpClass
import  logging, os

class App(object):

    def __init__(self, version, updater):
        # set version
        self.version = version

        # set updater
        self.updater = updater

        # read user defaults (preferences)
        self.prefs = prefs = NSUserDefaults.standardUserDefaults()

        # check if quotefixing should be turned on
        self.is_active = not prefs.bool["QuoteFixDisabled"]

        # check if debugging should be turned on
        self.is_debugging = prefs.bool["QuoteFixEnableDebugging"] and True or False

        # check if 'keep whitespace after attribution' is turned on
        self.keep_attribution_whitespace = prefs.bool["QuoteFixKeepAttributionWhitespace"] and True or False

        # check if 'remove trailing whitespace' is turned on
        self.remove_trailing_whitespace = prefs.bool["QuoteFixRemoveTrailingWhitespace"] and True or False

        # check for remove-quotes
        self.remove_quotes          = prefs.bool["QuoteFixRemoveQuotes"] and True or False
        self.remove_quotes_level    = prefs.int["QuoteFixRemoveQuotesLevel"] or 5

        # check for custom reply attribution
        self.use_custom_reply_attribution   = prefs.bool["QuoteFixUseCustomReplyAttribution"] and True or False
        self.custom_reply_attribution       = prefs.string["QuoteFixCustomReplyAttribution"] or ""

        # check for custom forwarding attribution
        self.use_custom_forwarding_attribution  = prefs.bool["QuoteFixUseCustomForwardingAttribution"] and True or False
        self.custom_forwarding_attribution      = prefs.string["QuoteFixCustomForwardingAttribution"] or ""

        # check update interval
        self.check_update_interval = prefs.int["QuoteFixCheckUpdateInterval"] or 0

        # inject menu
        self.menu = Menu.alloc().initWithApp_(self).inject()

        # demand-load preferences
        self.preferences_loaded = False

        # check if we're running in a different Mail version as before
        self.check_version()

    def check_version(self):
        infodict    = NSBundle.mainBundle().infoDictionary()
        mailversion = infodict['CFBundleVersion']
        lastknown   = self.prefs.string["QuoteFixLastKnownBundleVersion"]
        if lastknown and lastknown != mailversion:
            Alert.showAlert(self.menu,
                'QuoteFix plug-in',
                '''
The QuoteFix plug-in detected a different Mail.app version (perhaps you updated?).

If you run into any problems with regards to replying or forwarding mail, consider removing this plug-in (from ~/Library/Mail/Bundles/).

(This alert is only displayed once for each new version of Mail.app)
''', alert_style = NSInformationalAlertStyle)

        self.prefs.string["QuoteFixLastKnownBundleVersion"] = mailversion

    # show preferences window
    def show_preferences(self):
        # load preferences NIB for the first time
        if not self.preferences_loaded:
            resourcepath            = NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix').resourcePath()
            nibfile                 = os.path.join(resourcepath, "QuoteFixPreferences.nib")
            context                 = { NSNibTopLevelObjects : [] }
            NSBundle.loadNibFile_externalNameTable_withZone_(nibfile, context, None)

            self.preferences_window = filter(lambda _: isinstance(_, NSWindow), context[NSNibTopLevelObjects])[0]
            self.preferences_loaded = True

        # show preferences window
        if self.preferences_window:
            self.preferences_window.makeKeyAndOrderFront_(self)

    # used for debugging
    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, html):
        self._html = html

    # return reference to main window
    def window(self):
        return NSApplication.sharedApplication().mainWindow()

    # 'is plugin active?'
    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, active):
        # store in preferences
        self.prefs.bool["QuoteFixDisabled"] = not active
        self._is_active = active

    # debugging
    @property
    def is_debugging(self):
        return self._is_debugging

    @is_debugging.setter
    def is_debugging(self, debugging):
        # store in preferences
        self.prefs.bool["QuoteFixEnableDebugging"] = debugging
        self._is_debugging = debugging
        # set logger level
        logging.getLogger('').setLevel(self._is_debugging and logging.DEBUG or logging.WARNING)
        logging.debug('debug logging active')

    # 'keep whitespace after attribution'
    @property
    def keep_attribution_whitespace(self):
        return self._keep_attribution_whitespace

    @keep_attribution_whitespace.setter
    def keep_attribution_whitespace(self, keep):
        # store in preferences
        self.prefs.bool["QuoteFixKeepAttributionWhitespace"] = keep
        self._keep_attribution_whitespace = keep

    # 'remove trailing whitespace'
    @property
    def remove_trailing_whitespace(self):
        return self._remove_trailing_whitespace

    @remove_trailing_whitespace.setter
    def remove_trailing_whitespace(self, remove):
        # store in preferences
        self.prefs.bool["QuoteFixRemoveTrailingWhitespace"] = remove
        self._remove_trailing_whitespace = remove

    # 'remove quotes from level'
    @property
    def remove_quotes_level(self):
        return self._remove_quotes_level

    @remove_quotes_level.setter
    def remove_quotes_level(self, level):
        # store in preferences
        self.prefs.int["QuoteFixRemoveQuotesLevel"] = level
        self._remove_quotes_level = level

    # 'remove quotes from level'
    @property
    def remove_quotes(self):
        return self._remove_quotes

    @remove_quotes.setter
    def remove_quotes(self, remove):
        # store in preferences
        self.prefs.bool["QuoteFixRemoveQuotes"] = remove
        self._remove_quotes = remove

    # 'use custom reply attribution'
    @property
    def use_custom_reply_attribution(self):
        return self.is_active and self._use_custom_reply_attribution or False

    @use_custom_reply_attribution.setter
    def use_custom_reply_attribution(self, use):
        # store in preferences
        self.prefs.bool["QuoteFixUseCustomReplyAttribution"] = use
        self._use_custom_reply_attribution = use

    # 'custom reply attribution'
    @property
    def custom_reply_attribution(self):
        return self._custom_reply_attribution

    @custom_reply_attribution.setter
    def custom_reply_attribution(self, value):
        # store in preferences
        self.prefs.string["QuoteFixCustomReplyAttribution"] = value
        self._custom_reply_attribution = value

    # 'use custom forwarding attribution'
    @property
    def use_custom_forwarding_attribution(self):
        return self.is_active and self._use_custom_forwarding_attribution or False

    @use_custom_forwarding_attribution.setter
    def use_custom_forwarding_attribution(self, use):
        # store in preferences
        self.prefs.bool["QuoteFixUseCustomForwardingAttribution"] = use
        self._use_custom_forwarding_attribution = use

    # 'custom forwarding attribution'
    @property
    def custom_forwarding_attribution(self):
        return self._custom_forwarding_attribution

    @custom_forwarding_attribution.setter
    def custom_forwarding_attribution(self, value):
        # store in preferences
        self.prefs.string["QuoteFixCustomForwardingAttribution"] = value
        self._custom_forwarding_attribution = value

    # update-related properties
    @property
    def check_update_interval(self):
        return self._check_update_interval

    @check_update_interval.setter
    def check_update_interval(self, value):
        self._check_update_interval = value
        # set updater
        if   value == 0: interval = 0 # never
        elif value == 1: interval = 7 * 24 * 60 * 60 # weekly
        elif value == 2: interval = int(4.35 * 7 * 24 * 60 * 60) # monthly
        else           : return
        self.updater.check_update_interval = interval

    @property
    def last_update_check(self):
        return self.updater.last_update_check

    # check for updates
    def check_for_updates(self):
        self.updater.check_for_updates()

# make NSUserDefaults a bit more Pythonic
class NSUserDefaults(Category(lookUpClass('NSUserDefaults'))):

    @property
    def bool(self):     return DictProxy(self, 'bool')

    @property
    def string(self):   return DictProxy(self, 'string')

    @property
    def object(self):   return DictProxy(self, 'object')

    @property
    def int(self):      return DictProxy(self, 'int')

class DictProxy:

    def __init__(self, delegate, type):
        self.delegate   = delegate
        self.type       = type

    def __getitem__(self, item):
        return {
            'string'    : self.delegate.stringForKey_,
            'bool'      : self.delegate.boolForKey_,
            'object'    : self.delegate.objectForKey_,
            'int'       : self.delegate.integerForKey_,
        }[self.type](item)

    def __setitem__(self, item, value):
        {
            'string'    : self.delegate.setObject_forKey_, # no setString_forKey_
            'bool'      : self.delegate.setBool_forKey_,
            'object'    : self.delegate.setObject_forKey_,
            'int'       : self.delegate.setInteger_forKey_,
        }[self.type](value, item)

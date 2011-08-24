from    AppKit          import *
from    Foundation      import *
from    objc            import Category, lookUpClass
import  logging, os, re

class App(object):

    def __init__(self, version, updater):
        # set version
        self.version = version

        # set updater
        self.updater = updater

        # read user defaults (preferences)
        self.prefs = NSUserDefaults.standardUserDefaults()

        # set log level
        logging.getLogger('').setLevel(self.is_debugging and logging.DEBUG or logging.WARNING)
        if self.is_debugging:
            logging.debug('debug logging active')

        # check update interval
        self.check_update_interval = self.prefs.int["QuoteFixCheckUpdateInterval"] or 0

        # check if we're running in a different Mail version as before
        self.check_version()

    def check_version(self):
        infodict    = NSBundle.mainBundle().infoDictionary()
        mailversion = infodict['CFBundleVersion']
        lastknown   = self.prefs.string["QuoteFixLastKnownBundleVersion"]
        if lastknown and lastknown != mailversion:
            NSRunAlertPanel(
                'QuoteFix plug-in',
                '''
The QuoteFix plug-in detected a different Mail.app version (perhaps you updated?).

If you run into any problems with regards to replying or forwarding mail, consider removing this plug-in (from ~/Library/Mail/Bundles/).

(This alert is only displayed once for each new version of Mail.app)''',
                    None,
                    None,
                    None
            )
            self.prefs.string["QuoteFixLastKnownBundleVersion"] = mailversion

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
        return not self.prefs.bool["QuoteFixDisabled"]

    # debugging
    @property
    def is_debugging(self):
        return self.prefs.bool['QuoteFixEnableDebugging']

    # 'is quotefixing enabled?'
    @property
    def is_quotefixing(self):
        return not self.prefs.bool["QuoteFixQuoteFixingDisabled"]

    # 'keep whitespace after attribution'
    @property
    def keep_attribution_whitespace(self):
        return self.prefs.bool["QuoteFixKeepAttributionWhitespace"]

    # 'remove trailing whitespace'
    @property
    def remove_trailing_whitespace(self):
        return self.prefs.bool["QuoteFixRemoveTrailingWhitespace"]

    # 'remove quotes from level'
    @property
    def remove_quotes(self):
        return self.prefs.bool["QuoteFixRemoveQuotes"]

    # 'remove quotes from level'
    @property
    def remove_quotes_level(self):
        return self.prefs.int["QuoteFixRemoveQuotesLevel"]

    # 'use custom reply attribution'
    @property
    def use_custom_reply_attribution(self):
        return self.is_active and self.prefs.bool["QuoteFixUseCustomReplyAttribution"] or False

    # 'custom reply attribution'
    @property
    def custom_reply_attribution(self):
        return self.prefs.string["QuoteFixCustomReplyAttribution"] or ""

    # 'increase quotelevel with custom reply'
    @property
    def custom_reply_increase_quotelevel(self):
        return self.prefs.bool["QuoteFixCustomReplyIncreaseQuoteLevel"] or False

    # 'custom reply is HTML code'
    @property
    def custom_reply_is_html(self):
        return self.prefs.bool["QuoteFixCustomReplyIsHTML"] or False

    # 'use custom forwarding attribution'
    @property
    def use_custom_forwarding_attribution(self):
        return self.is_active and self.prefs.bool["QuoteFixUseCustomForwardingAttribution"] or False

    # 'custom forwarding attribution'
    @property
    def custom_forwarding_attribution(self):
        return self.prefs.string["QuoteFixCustomForwardingAttribution"] or ""

    # 'increase quotelevel with custom forwarding'
    @property
    def custom_forwarding_increase_quotelevel(self):
        return self.prefs.bool["QuoteFixCustomForwardingIncreaseQuoteLevel"] or False

    # 'custom forwarding is HTML code'
    @property
    def custom_forwarding_is_html(self):
        return self.prefs.bool["QuoteFixCustomForwardingIsHTML"] or False

    # 'enable templating in customized attributions'
    @property
    def custom_attribution_allow_templating(self):
        return self.prefs.bool["QuoteFixCustomAttributionAllowTemplating"] or False

    # signature matcher
    @property
    def signature_matcher(self):
        # use custom matcher?
        if self.prefs.bool["QuoteFixUseCustomSignatureMatcher"]:
            matcher = self.prefs.string["QuoteFixCustomSignatureMatcher"]
        else:
            matcher = self.default_signature_matcher

        # try to compile regular expression to catch errors early
        try:
            re.compile(matcher)
        except re.error, e:
            matcher = self.default_signature_matcher
            NSRunAlertPanel(
                'QuoteFix plug-in',
                'The supplied custom signature matcher contains an invalid regular expression (error: "%s").\n\nI will revert back to the default matcher until the problem is fixed in the preferences.' % str(e),
                None, None, None)

        # return compiled regex
        return re.compile(matcher)

    @property
    def default_signature_matcher(self):
        return r'(?i)--(?:&nbsp;|\s+|\xa0)?$'

    # update-related properties
    @property
    def check_update_interval(self):
        return self._check_update_interval

    @check_update_interval.setter
    def check_update_interval(self, value):
        # store in preferences
        self.prefs.string["QuoteFixCheckUpdateInterval"] = value
        self._check_update_interval = value

        # convert to interval and pass to updater
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

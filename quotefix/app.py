from    AppKit                  import *
from    Foundation              import *
from    quotefix.messagetypes   import *
from    quotefix.menu           import Menu
from    objc                    import Category, lookUpClass
import  logging, os, re

class App(object):

    def __init__(self, version, updater):
        # set version
        self.version = version

        # set updater
        self.updater = updater

        # keep state of 'toggle key'
        self.toggle_key_active = False

        # read user defaults (preferences)
        self.prefs = NSUserDefaults.standardUserDefaults()

        # register some default values
        self.prefs.registerDefaults_(dict(
            QuoteFixFixReply        = True,
            QuoteFixFixReplyAll     = True,
            QuoteFixFixForward      = True,
            QuoteFixFixDraft        = False,
            QuoteFixFixNewMessage   = False,
        ))

        # set log level
        logging.getLogger('').setLevel(self.is_debugging and logging.DEBUG or logging.WARNING)
        if self.is_debugging:
            logging.debug('debug logging active')

        # add menu item for quick enable/disable
        Menu.alloc().initWithApp_(self).inject()

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

    @is_active.setter
    def is_active(self, value):
        self.prefs.bool["QuoteFixDisabled"] = value

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

    # 'remove from last occurrance of possible signature match'
    @property
    def remove_from_last_signature_match(self):
        return self.prefs.bool["QuoteFixRemoveSignatureFromLastMatch"]

    # 'remove trailing whitespace'
    @property
    def remove_trailing_whitespace(self):
        return self.prefs.bool["QuoteFixRemoveTrailingWhitespace"]

    # 'keep leading whitespace'
    @property
    def keep_leading_whitespace(self):
        return self.prefs.bool['QuoteFixKeepLeadingWhitespace']

    # 'make selectable quotes'
    @property
    def selectable_quotes(self):
        return self.prefs.bool['QuoteFixMakeSelectableQuotes']

    # 'remove attachment placeholders'
    @property
    def remove_attachment_placeholders(self):
        return self.prefs.bool["QuoteFixRemoveAttachmentPlaceholders"]

    # 'remove quotes from level'
    @property
    def remove_quotes(self):
        return self.prefs.bool["QuoteFixRemoveQuotes"]

    # 'remove quotes from level'
    @property
    def remove_quotes_level(self):
        return self.prefs.int["QuoteFixRemoveQuotesLevel"]

    # message types to perform quotefixing on
    @property
    def message_types_to_quotefix(self):
        types = []
        if self.prefs.bool["QuoteFixFixReply"]:         types.append(REPLY)
        if self.prefs.bool["QuoteFixFixReplyAll"]:      types.append(REPLY_ALL)
        if self.prefs.bool["QuoteFixFixForward"]:       types.append(FORWARD)
        if self.prefs.bool["QuoteFixFixDraft"]:         types.append(DRAFT)
        if self.prefs.bool["QuoteFixFixNewMessage"]:    types.append(NEW)
        return types

    # 'don't add extra line of whitespace below first-level quote'
    @property
    def no_whitespace_below_quote(self):
        return self.prefs.bool["QuoteFixNoWhitespaceBelowQuote"]

    # 'move cursor to top of document after quotefixing'
    @property
    def move_cursor_to_top(self):
        return self.prefs.bool["QuoteFixMoveCursorToTop"]

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

    # 'convert reply to rich text when needed?'
    @property
    def custom_reply_convert_to_rich(self):
        return self.prefs.bool['QuoteFixCustomReplyConvertToRichText'] or False

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

    # 'remove Apple Mail forward attribution'
    @property
    def remove_apple_mail_forward_attribution(self):
        return self.prefs.bool["QuoteFixRemoveAppleMailForwardAttribution"] or False

    # 'custom forwarding is HTML code'
    @property
    def custom_forwarding_is_html(self):
        return self.prefs.bool["QuoteFixCustomForwardingIsHTML"] or False

    # 'convert forwarded message to rich text when needed?'
    @property
    def custom_forwarding_convert_to_rich(self):
        return self.prefs.bool['QuoteFixCustomForwardingConvertToRichText'] or False

    # 'enable templating in customized attributions'
    @property
    def custom_attribution_allow_templating(self):
        return self.prefs.bool["QuoteFixCustomAttributionAllowTemplating"] or False

    # 'keep senders signature'
    @property
    def keep_sender_signature(self):
        return self.prefs.bool["QuoteFixKeepSenderSignature"] or False

    # signature matcher
    @property
    def signature_matcher(self):
        matcher = None
        # use custom matcher?
        if self.prefs.bool["QuoteFixUseCustomSignatureMatcher"]:
            matcher = self.prefs.string["QuoteFixCustomSignatureMatcher"]
        if not matcher:
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

    # handle warning message generated with customized attributions
    @property
    def dont_show_html_attribution_warning(self):
        return self.prefs.string["QuoteFixDontShowHTMLAttributionWarning"]

    @dont_show_html_attribution_warning.setter
    def dont_show_html_attribution_warning(self, value):
        self.prefs.string["QuoteFixDontShowHTMLAttributionWarning"] = value

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
        self.updater.set_update_interval(interval)

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

from    AppKit          import *
from    Foundation      import *
import  PyObjCTools.AppHelper, objc, traceback

class Alert:

    @classmethod
    def showAlert(cls, sender, title, msg, alert_style = NSWarningAlertStyle):
        alert = NSAlert.alloc().init()
        alert.addButtonWithTitle_('Ok')
        alert.setMessageText_(title)
        alert.setInformativeText_(msg)
        alert.setAlertStyle_(alert_style)
        alert.beginSheetModalForWindow_modalDelegate_didEndSelector_contextInfo_(sender.window(), sender, "", 0)

    @classmethod
    def showException(cls, sender):
        cls.showAlert(
            sender,
            'QuoteFix caught an exception',
            'The QuoteFix plug-in caught an exception:\n\n' +
            traceback.format_exc() +
            '\nPlease contact the developer quoting the contents of this alert.',
        )

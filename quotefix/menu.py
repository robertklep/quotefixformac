from    AppKit          import *
from    Foundation      import *
import  objc

class Menu(NSObject):

    def initWithApp_(self, app):
        self = super(Menu, self).init()
        if self is None:
            return None
        self.app        = app
        self.mainwindow = NSApplication.sharedApplication().mainWindow()
        self.bundle     = NSBundle.bundleWithIdentifier_('name.klep.mail.QuoteFix')
        return self

    def inject(self):
        try:
            # necessary because of the menu callbacks
            self.retain()

            # get application menu instance
            appmenu = NSApplication.sharedApplication().mainMenu().itemAtIndex_(0).submenu()

            # make a new menu item
            self.item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "QuoteFix",
                "toggleState:",
                "")
            self.item.setToolTip_(self.get_string("QUOTEFIX_TOOLTIP", ""))
            self.set_state_and_title(self.item)
            self.item.setTarget_(self)

            # add separator and new item
            appmenu.insertItem_atIndex_(NSMenuItem.separatorItem(), 1)
            appmenu.insertItem_atIndex_(self.item, 2)

            # observe changes for active state
            NSUserDefaultsController.sharedUserDefaultsController().addObserver_forKeyPath_options_context_(
                self,
                "values.QuoteFixDisabled",
                NSKeyValueObservingOptionNew,
                None
            )

        except Exception, e:
            raise e
        return self

    def set_state_and_title(self, item):
        item.setState_(self.app.is_active)
        item.setTitle_(self.get_string(
            self.app.is_active and "QuoteFix is enabled" or "QuoteFix is disabled"
        ))
        item.setState_(self.app.is_active)

    def get_string(self, key, fallback = None):
        if fallback is None:
            fallback = key
        return self.bundle.localizedStringForKey_value_table_(key, fallback, None)

    def toggleState_(self, sender):
        self.app.is_active = sender.state()
        self.set_state_and_title(sender)

    def window(self):
        return self.mainwindow

    # update menu item when active state of plug-in changes
    def observeValueForKeyPath_ofObject_change_context_(self, keyPath, obj, change, context):
        self.set_state_and_title(self.item)

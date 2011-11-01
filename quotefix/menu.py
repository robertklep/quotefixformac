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
        return self

    def inject(self):
        try:
            # necessary because of the menu callbacks
            self.retain()

            # get application menu instance
            appmenu = NSApplication.sharedApplication().mainMenu().itemAtIndex_(0).submenu()

            # make a new menu item
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "QuoteFix",
                "toggleState:",
                "")
            self.set_state_and_title(item)
            item.setTarget_(self)

            # add separator and new item
            appmenu.insertItem_atIndex_(NSMenuItem.separatorItem(), 1)
            appmenu.insertItem_atIndex_(item, 2)

        except Exception, e:
            raise e
        return self

    def set_state_and_title(self, item):
        item.setState_(self.app.is_active)
        item.setTitle_("QuoteFix is %s" % (self.app.is_active and "enabled" or "disabled"))
        item.setState_(self.app.is_active)

    def toggleState_(self, sender):
        self.app.is_active = sender.state()
        self.set_state_and_title(sender)

    def window(self):
        return self.mainwindow

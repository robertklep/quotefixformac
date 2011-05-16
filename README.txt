QuoteFix for Mac
================

What is it?
-----------

QuoteFix is a plug-in for Mail.app which fixes some issues with replying to
e-mail:

- it tries to remove the signature from the original message (but check
  here to see why it doesn't always succeed)
- it removes certain unnecessary empty lines
- it positions the cursor below the original message, instead of above
  it (in other words, bottom-posting instead of top-posting)
- it can (optionally) prune nested quotes from a specific level and
  above

Installing the plug-in
----------------------
Before installing the plug-in, you'll need to make sure that Mail.app's
plug-in support is turned on. For this, execute the following two commands
in Terminal.app:

  defaults write com.apple.mail EnableBundles -bool true
  defaults write com.apple.mail BundleCompatibilityVersion 3

Next, download the plug-in (pick the binary version) and unpack it in
~/Library/Mail/Bundles/

Lastly, quit Mail.app if it's running, and start it up again.

In case you run into any problems, just remove QuoteFix.mailbundle from the
bundle-folder and restart Mail.app.

Licence & Copyright
-------------------

This plugin is written by Robert Klep (robert@klep.name) and is provided
"as-is", without *any* warranties whatsoever.

QuoteFix' downloads and support is hosted by Google at
http://code.google.com/p/quotefixformac/

It uses the Sparkle framework from to provide software updates, which comes
with the following permission notice:

        Copyright (c) 2006 Andy Matuschak

        Permission is hereby granted, free of charge, to any person
        obtaining a copy of this software and associated documentation
        files (the "Software"), to deal in the Software without
        restriction, including without limitation the rights to use,
        copy, modify, merge, publish, distribute, sublicense, and/or
        sell copies of the Software, and to permit persons to whom the
        Software is furnished to do so, subject to the following
        conditions:

        The above copyright notice and this permission notice shall be
        included in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
        EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
        OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
        HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
        WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
        FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
        OTHER DEALINGS IN THE SOFTWARE.

See also: http://sparkle.andymatuschak.org/

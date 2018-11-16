# QuoteFix for Mac <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4UF2KB2BTW6AC"><img style="vertical-align:middle; opacity:0.3" src="https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif"></a>

## _Important notice_

I decided to not accept requests for new features for the time being, primarily due to lack of time. Any feature requests will be closed (but tagged so if things quiet down, I can reopen them).

However, do keep submitting bug reports. I'll try and fix them as fast as I can.

## Latest releases

The latest release can always be found [here](https://github.com/robertklep/quotefixformac/releases/).

* [v2.10.0-alpha.1](https://github.com/robertklep/quotefixformac/releases/tag/v2.10.0-alpha.1): Mojave support
* [v2.9.0](https://github.com/robertklep/quotefixformac/releases/tag/v2.9.0): Official 2.9.0 release
* [v2.9.0-alpha.1](https://github.com/robertklep/quotefixformac/releases/tag/v2.9.0-alpha.1): High Sierra support
* [v2.8.0](https://github.com/robertklep/quotefixformac/releases/tag/v2.8.0): Official 2.8.0 release
* [v2.8.0-alpha.6](https://github.com/robertklep/quotefixformac/releases/tag/v2.8.0-alpha.6): Sierra 10.12.4 support
* [v2.8.0-alpha.5](https://github.com/robertklep/quotefixformac/releases/tag/v2.8.0-alpha.5): bugfixes
* [v2.8.0-alpha.4](https://github.com/robertklep/quotefixformac/releases/tag/v2.8.0-alpha.4): bugfixes
* [v2.8.0-alpha.3](https://github.com/robertklep/quotefixformac/releases/tag/v2.8.0-alpha.3): Sierra 10.12.2 (beta) support (also works for 10.12.2 final)
* [v2.8.0-alpha.2](https://github.com/robertklep/quotefixformac/releases/tag/v2.8.0-alpha.2): Sierra 10.12.1 (beta) support
* [v2.8.0-alpha.1](https://github.com/robertklep/quotefixformac/releases/tag/v2.8.0-alpha.1): Sierra support
* [v2.7.4](https://github.com/robertklep/quotefixformac/releases/tag/v2.7.4): support for 10.11.4
* [v2.7.3](https://github.com/robertklep/quotefixformac/releases/tag/v2.7.3): somewhat fixes #57
* [v2.7.2](https://github.com/robertklep/quotefixformac/releases/tag/v2.7.2): support for 10.11.2
* [v2.7.1](https://github.com/robertklep/quotefixformac/releases/tag/v2.7.1): minor update to enable logging of template errors
* [v2.7.0](https://github.com/robertklep/quotefixformac/releases/tag/v2.7.0): official 10.11 (El Capitan) support
* [v2.6.0](https://github.com/robertklep/quotefixformac/releases/tag/v2.6.0): official 10.10 support, plus rewrites of several parts of the plug-in
* [v2.5.7](https://github.com/robertklep/quotefixformac/releases/tag/v2.5.7): fixes #21
* [v2.5.6](https://github.com/robertklep/quotefixformac/releases/tag/v2.5.6): 10.9.4 support
* [v2.5.5](https://github.com/robertklep/quotefixformac/releases/tag/v2.5.5): bugfixes
* [v2.5.4](https://github.com/robertklep/quotefixformac/releases/tag/v2.5.4): 10.9.3 support
* [v2.5.3](https://github.com/robertklep/quotefixformac/releases/tag/v2.5.3): 10.9.2 support
* [v2.5.2](https://github.com/robertklep/quotefixformac/releases/tag/v2.5.2): fixed bug in date formatting
* [v2.5.1](https://github.com/robertklep/quotefixformac/releases/tag/v2.5.1): 10.9.1 support

## FAQ

See [the wiki](https://github.com/robertklep/quotefixformac/wiki/FAQ---Frequently-Asked-Questions).

## What is it?

QuoteFix is a plug-in for Mail.app which fixes some issues with replying to
e-mail:

* it tries to remove the signature from the original message;
* it removes certain unnecessary empty lines;
* it positions the cursor below the original message, instead of above it (in other words, bottom-posting instead of top-posting);
* it can (optionally) prune nested quotes from a specific level and above;

It also provides customized attributions for replies and forwards.

## Installation

Before installing the plug-in, you'll need to make sure that Mail.app's
plug-in support is turned on. For this, execute the following two commands
in Terminal.app:
```
defaults write ~/Library/Containers/com.apple.mail/Data/Library/Preferences/com.apple.mail.plist EnableBundles -bool true
defaults write ~/Library/Containers/com.apple.mail/Data/Library/Preferences/com.apple.mail.plist BundleCompatibilityVersion 4
```

Next, perform the following steps:

* Download the plugin if you haven't done so already
* Navigate in Finder to `~/Library/Mail/` (where `~` means: your home directory)
* If a `Bundles` folder doesn't yet exist, create an empty one
* Extract the downloaded ZIP file and copy `QuoteFix.mailbundle` into the Bundles folder
* Lastly, quit Mail.app if it's running, and start it up again.

In case you run into any problems, or want to uninstall QuoteFix, just
remove QuoteFix.mailbundle from the bundle-folder and restart Mail.app.

## Usage

After installation, QuoteFix is enabled. It will perform its magic
automatically when you reply to, or forward, messages.

The behaviour of the plug-in is customizable via its preferences. QuoteFix
has it's own preference pane in the preferences window of Mail.app. Most
preferences speak for themselves, or have a useful tooltip which pops up
when you hover the cursor above it.

If you temporarily want to turn off QuoteFix, but don't want to uninstall
it, check off the *QuoteFix is enabled* checkbox. As of version 2.3.1,
(de)activating QuoteFix can be done from a menu item in the Mail menu. You
could use [the standard way of assigning a keyboard shortcut to a menu item
in Mac OS X](http://lifehacker.com/343328/create-a-keyboard-shortcut-for-any-menu-action-in-any-program) to enable or disable QuoteFix with a keyboard shortcut.

## Customized Attributions

QuoteFix also provides the ability to define your own attribution lines
(the first line of a reply/forward, usually looking something like
`On SOME DATE, at SOME TIME, SOMEONE wrote:`).

Customized attributions work by way of templates: you define a template in
the preferences, and parts of the template will – at the time of replying
or forwarding – be replaced by values reflecting parts of the message you
are replying to or forwarding.

Templating works by replacing template variables with values. A template
variable looks like this: `${VARIABLE}`. It will be replaced with a value
depending on what `VARIABLE` contains.

A (non-exhaustive) list of variables you can use:

<table border=0>
    <tr>
        <td valign="top"><code>${message.from}</code></td>
        <td>
            Name and e-mail address of sender of message:<br/>
            <i>Your Friend &lt;yourfriend@example.com&gt;</i>
        </td>
    </tr>
    <tr>
        <td valign="top"><code>${message.from.name}</code></td>
        <td>
            Name of sender of message:<br/>
            <i>Your Friend</i>
        </td>
    </tr>
    <tr>
        <td valign="top"><code>${message.from.email}</code></td>
        <td>
            E-mail address of sender of message:<br/>
            <i>yourfriend@example.com</i>
        </td>
    </tr>
    <tr>
        <td valign="top"><code>${message.to}</code></td>
        <td>
            Your e-mail address (this is the address that was used for
            the message to reach you). This is more like the
            <code>Delivered-To</code> header than the <code>To</code>
            header (for that, see <code>${message.recipients}</code>)
        </td>
    </tr>
    <tr>
        <td valign="top"><code>${message.recipients}</code></td>
        <td>
            A list of all the recipients of the message, as mentioned in
            both the <code>To</code> and <code>Cc</code> headers.
        </td>
    </tr>
    <tr>
        <td valign="top"><code>${message.recipients.to}</code></td>
        <td>
            A list of the recipients of the message mentioned in
            the <code>To</code> header.
        </td>
    </tr>
    <tr>
        <td valign="top"><code>${message.recipients.cc}</code></td>
        <td>
            A list of the recipients of the message mentioned in
            the <code>Cc</code> header.
        </td>
    </tr>
    <tr>
        <td valign="top"><code>${message.subject}</code></td>
        <td>The subject of the message.</td>
    </tr>
    <tr>
        <td valign="top">
            <code>${message.sent}</code><br/>
            <code>${message.received}</code>
        </td>
        <td>
            Sent/received timestamps. If you want more finegrained
            control over formatting timestamps, these variables split
            into separate fields: <code>year</code>, <code>month</code>,
            <code>day</code>, <code>hour</code>, <code>hour12</code>,
            <code>ampm</code>, <code>minute</code>, <code>second</code>,
            <code>weeknumber</code>, <code>monthshort</code>,
            <code>monthlong</code>, <code>dayshort</code>,
            <code>daylong</code>, <code>date</code>, <code>time</code>.<br/>
            Use these like so: <code>${message.sent.year}</code>.
            <p><a href="#advanced-datetime-formatting">See below for more advanced date/time formatting
                options.</a></p>
        </td>
    </tr>
</table>

If you want even more freedom in formatting attribution lines, there's an
experimental feature (which can be enabled in the *Advanced* preferences)
which enables conditional statements, string/date formatting, and much
more. This is based on a modified version of the [pyratemp](http://www.simple-is-better.org/template/pyratemp.html) templating
library for Python written by Roland Koebler.

A small example of what's possible:
```
From: ${message.from}
{% if message.recipients.to %}
 To: ${message.recipients.to.join("; ", "name")}
{% end %}
{% if message.recipients.cc %}
 Cc: ${message.recipients.cc.join("; ", "name")}
{% end %}
Subject: ${message.subject.lower()}
Sent-Date: ${message.sent.strftime("%d-%m-%Y")}
```

You can also enable HTML-formatting for your custom attributions. For this
to work, the (outgoing) message format should be *Rich Text*. You can have
QuoteFix automatically convert a message to Rich Text if your attribution
should be interpreted in HTML. Otherwise, QuoteFix will issue a warning.

If you want to mimic the attribution generated by Outlook, try this (with
HTML-formatting enabled):
```
<b>From:</b> ${message.from}
<b>Date:</b> ${message.received}
<b>To:</b> ${message.to}
<b>Subject:</b> ${message.subject}
```
When you're editing your customized attribution, QuoteFix will generate an
approximate preview as tooltip of the text field you're entering the
attribution in.

## Advanced date/time formatting

If you want even more finegrained control over the formatting of dates and
times, you can enable *"advanced templating"* in the Advanced preferences,
after which date/time variables like `message.sent` and `message.received`
will have `.format()` and `.strftime()` methods with which you can format the
output of the objects.

Functionally, these two methods perform the same operation – namely
formatting date/time objects – the difference is in the formatting strings
used:

*  `.strftime()` uses the common Unix function with the same name for
   formatting. [Look here for more information](http://docs.python.org/library/time.html#time.strftime).
*  `.format()` uses the Unicode date format patterns. [Look here for more
   information](http://unicode.org/reports/tr35/tr35-10.html#Date_Format_Patterns).

An example:
```
${message.sent.format("EEE MMM dd yyyy HH:mm:ss")}
```
This will output: `Sun Nov 06 2011 10:19:34`

Similarly, with `.strftime()`:
```
${message.sent.strftime("%a %b %d %Y %H:%M:%S")}
```

However: the output will be generated in the current locale, which means
that it will be formatted according to your local language settings.

To change this, both methods accept a second argument: a locale
identifier. You can use it to convert the output to a certain locale,
instead of the default locale (which can be changed in the *System
Preferences* of Mac OS X: *Language & Text > Formats*).

The same example as above, but with a different locale:
```
${message.sent.format("EEE MMM dd yyyy HH:mm:ss", 'fr_FR')}
```
The output: `dim. nov. 06 2011 10:19:34`

If you want the default format, just in a different locale, use the
`.locale()` method:
```
${message.sent.locale('fr_FR')}
```

## Enabling/disabling the plug-in

QuoteFix has various ways of turning off its behaviour, short of
uninstalling it:

* You can turn QuoteFix off from its preferences; this will disable the plug-in until you enable it again;
* You can quickly turn the plug-in on/off from the Mail menu. If you want, you can even assign a keyboard shortcut to this menu item from System Preferences;
* You can toggle the enable (or disable) status of QuoteFix for a single message by pressing down `Option` whilst initiating a Reply/Forward action. That is:
    * When QuoteFix is **disabled**, pressing `Option` will *enable* QuoteFix for that particular message only;
    * Likewise: when QuoteFix is **enabled**, pressing `Option` will *disable* QuoteFix for that particular message only;

## Building the plug-in

If you want to build the plug-in yourself, ideally you need to use a non-system Python interpreter (although not *strictly* necessary if you want to use the plug-in on your system only).

I use Python 2.7.5 as installed by [Homebrew](http://brew.sh/). I also use [virtualenv](https://pypi.python.org/pypi/virtualenv/) to create a clean environment in which to build the plug-in.

Make sure the following requirements are installed:
```
pip install pyobjc # might take some time
pip install py2app
```

Next, clone the repository:
```
git clone https://github.com/robertklep/quotefixformac.git
```

And build the plug-in:
```
cd quotefixformac
python setup.py py2app
```

This will build the plug-in, which can be located in `dist/`.

## Licence & copyright

This plugin is written by Robert Klep and is provided "as-is", without any
warranties whatsoever.

QuoteFix source, downloads and support is hosted by GitHub at
https://github.com/robertklep/quotefixformac

QuoteFix uses the Sparkle framework from Andy Matuschak to provide software
updates, which comes with the following permission notice:

>  Copyright (c) 2006 Andy Matuschak Permission is hereby granted, free of
>  charge, to any person obtaining a copy of this software and associated
>  documentation files (the "Software"), to deal in the Software without
>  restriction, including without limitation the rights to use, copy,
>  modify, merge, publish, distribute, sublicense, and/or sell copies of
>  the Software, and to permit persons to whom the Software is furnished to
>  do so, subject to the following conditions: The above copyright notice
>  and this permission notice shall be included in all copies or
>  substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
>  WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
>  LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
>  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
>  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
>  AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
>  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
>  SOFTWARE.

See also [http://sparkle.andymatuschak.org/](http://sparkle.andymatuschak.org/).

# Like Quotefix?

Consider making a donation: <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4UF2KB2BTW6AC"><img style="vertical-align:middle" src="https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif"></a>

ETH: 0x93eaE7ad708EF996bdd2d03d42D10dB278E29172	

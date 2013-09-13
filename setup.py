from    distutils.core  import setup
from    glob            import glob
import  py2app, sys, os, commands

# overriding version?
if 'QUOTEFIX_VERSION' in os.environ:
    hgversion = os.environ['QUOTEFIX_VERSION']
else:
    # determine version by latest tag
    status, hgtags = commands.getstatusoutput("env VERSIONER_PYTHON_VERSION= hg tags 2>/dev/null | grep -v '^tip' | head -1")
    if status != 0:
        # probably no hg installed or not building from a repository
        hgversion = "unknown"
    else:
        hgversion = hgtags.split()[0]

# define distutils setup structure
setup(
    plugin      = [ 'QuoteFix.py' ],
    version     = hgversion,
    description = "QuoteFix for Mac is a Mail.app plugin",
    data_files  = [
        'English.lproj',
        'Dutch.lproj',
        'French.lproj',
        'updates/quotefix.sparkle.pub.pem',
        'resources/donate.gif'
    ],
    options     = dict(py2app = dict(
        extension       = '.mailbundle',
        semi_standalone = False,
        packages        = [ 'quotefix' ],
        frameworks      = glob("frameworks/*.framework"),
        plist           = dict(
            NSPrincipalClass                    = 'QuoteFix',
            CFBundleIdentifier                  = 'name.klep.mail.QuoteFix',
            NSHumanReadableCopyright            = '(c) 2009, 2010, 2011, 2012 Robert Klep, robert@klep.name',
            SupportedPluginCompatibilityUUIDs   = [
                # 10.6
                '225E0A48-2CDB-44A6-8D99-A9BB8AF6BA04', # Mail 4.0
                'B3F3FC72-315D-4323-BE85-7AB76090224D', # Message.framework 4.0
                # 10.6.1
                '2610F061-32C6-4C6B-B90A-7A3102F9B9C8', # Mail 4.1
                '99BB3782-6C16-4C6F-B910-25ED1C1CB38B', # Message.framework 4.1
                # 10.6.2
                '2F0CF6F9-35BA-4812-9CB2-155C0FDB9B0F', # Mail
                '0CB5F2A0-A173-4809-86E3-9317261F1745', # Message.framework
                # 10.6.4
                'B842F7D0-4D81-4DDF-A672-129CA5B32D57', # Mail 4.3
                'E71BD599-351A-42C5-9B63-EA5C47F7CE8E', # Message.framework 4.3
                # 10.6.5
                'BDD81F4D-6881-4A8D-94A7-E67410089EEB', # Mail 4.4
                '857A142A-AB81-4D99-BECC-D1B55A86D94E', # Message.framework 4.4
                # special case for Mail 4.4.1
                '36555EB0-53A7-4B29-9B84-6C0C6BACFC23',
                # 10.6.7
                '9049EF7D-5873-4F54-A447-51D722009310',
                '1C58722D-AFBD-464E-81BB-0E05C108BE06',
                # 10.7 (Lion)
                '2DE49D65-B49E-4303-A280-8448872EFE87',
                '1146A009-E373-4DB6-AB4D-47E59A7E50FD',
                # 10.7.2
                '6E7970A3-E5F1-4C41-A904-B18D3D8FAA7D',
                'EF59EC5E-EFCD-4EA7-B617-6C5708397D24',
                # 10.7.3
                '4C286C70-7F18-4839-B903-6F2D58FA4C71',
                # Mountain Lion 10.8 12A128p
                '608CE00F-4576-4CAD-B362-F3CCB7DE8D67',
                # 10.6.8 (Mail 4.6)
                '064442B6-53C0-4A97-B71B-2F111AE4195B',
                '588FF7D1-4310-4175-9980-145B7E975C02',
                # 10.7.5
                '758F235A-2FD0-4660-9B52-102CD0EA897F',
                '3335F782-01E2-4DF1-9E61-F81314124212',
                # 10.8.4
                '2183B2CD-BEDF-4AA6-AC18-A1BBED2E3354',
                '19B53E95-0964-4AAB-88F9-6D2F8B7B6037',
                # 10.8.5
                '2B98D2DD-000B-4521-83EB-7BFCB9B161C8',
                'DAFFB2B4-77BC-4C25-8CE1-2405E652D54B'
            ],
            # settings for Sparkle
            SUFeedURL = 'http://quotefix.quotefixformac.googlecode.com/hg/updates/appcast.xml',
            #SUFeedURL = 'http://localhost:8000/appcast.xml',
            SUEnableAutomaticChecks = False,
            SUShowReleaseNotes = True,
            SUPublicDSAKeyFile = 'quotefix.sparkle.pub.pem',
            SUAllowsAutomaticUpdates = False,
        )
    ))
)

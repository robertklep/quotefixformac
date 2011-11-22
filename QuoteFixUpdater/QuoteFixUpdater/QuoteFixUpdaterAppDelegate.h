//
//  QuoteFixUpdaterAppDelegate.h
//  QuoteFixUpdater
//
//  Created by Robert Klep on 21-11-11.
//  Copyright 2011 Robert Klep. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import <Sparkle/Sparkle.h>

@interface QuoteFixUpdaterAppDelegate : NSObject <NSApplicationDelegate> {
    NSWindow        *window;
    NSConnection    *connection;
    NSBundle        *updatebundle;
    NSString        *relaunchpath;
    SUUpdater       *updater;
}
- (void) startProxy;
- (BOOL) initializeForBundle:(NSBundle *)bundle relaunchPath:(NSString *)path;
- (NSDate *) lastUpdateCheckDate;
- (void) checkForUpdatesInBackground;
- (BOOL) updateInProgress;

- (void) updater:(SUUpdater *)updater didFinishLoadingAppcast:(SUAppcast *)appcast;
- (void) updater:(SUUpdater *)updater didFindValidUpdate:(SUAppcastItem *)update;
- (void) updaterDidNotFindUpdate:(SUUpdater *)update;
- (NSString *) pathToRelaunchForUpdater:(SUUpdater *)updater;

- (NSString *) helloWorld;
- (void) quit;

@property (assign) IBOutlet NSWindow *window;

@end

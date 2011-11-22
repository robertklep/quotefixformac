//
//  QuoteFixUpdaterAppDelegate.m
//  QuoteFixUpdater
//
//  Created by Robert Klep on 21-11-11.
//  Copyright 2011 Robert Klep. All rights reserved.
//

#import "QuoteFixUpdaterAppDelegate.h"

@implementation QuoteFixUpdaterAppDelegate

@synthesize window;

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
    NSLog(@"QuoteFixUpdater starting");
    [self startProxy];
}

- (void) startProxy {
    NSPort *port = [NSPort port];
    
    connection = [[[NSConnection alloc] initWithReceivePort:port sendPort:nil] retain];
    [connection setRootObject:self];
    [connection registerName:@"QuoteFixUpdater"];
    NSLog(@"QuoteFixUpdater waiting for commands...");
}

- (BOOL) initializeForBundle:(NSBundle *)bundle relaunchPath:(NSString *)path {
    updatebundle = [bundle retain];
    relaunchpath = [path retain];
    updater = [[SUUpdater updaterForBundle:updatebundle] retain];
    [updater setDelegate:self];
    [updater resetUpdateCycle];
    return YES;
}

- (NSDate *) lastUpdateCheckDate {
    return [updater lastUpdateCheckDate];
}

- (void) checkForUpdatesInBackground {
    NSLog(@"QuoteFixUpdater going to check for updates, url = %@", [[updater feedURL] absoluteString]);
    [updater checkForUpdatesInBackground];
}

- (BOOL) updateInProgress {
    return [updater updateInProgress];
}

- (void) updater:(SUUpdater *)updater didFinishLoadingAppcast:(SUAppcast *)appcast {
    NSLog(@"QuoteFixUpdater did finish loading appcast %@", appcast);
}

- (void) updater:(SUUpdater *)updater didFindValidUpdate:(SUAppcastItem *)update {
    NSLog(@"QuoteFixUpdater did find valid update %@", update);
}

- (void) updaterDidNotFindUpdate:(SUUpdater *)update {
    NSLog(@"QuoteFixUpdater did not find update %@", update);
}

- (NSString *) pathToRelaunchForUpdater:(SUUpdater *)updater {
    return relaunchpath;
}

- (NSString *) helloWorld {
    return @"Hello, world!";
}

- (void) quit {
    NSLog(@"QuoteFixUpdater received quit message");
    [connection invalidate];
    [NSApp terminate:self];
}

-(void)dealloc {
    [connection release];
    [updatebundle release];
    [relaunchpath release];
    [updater release];

    [super dealloc];
}

@end

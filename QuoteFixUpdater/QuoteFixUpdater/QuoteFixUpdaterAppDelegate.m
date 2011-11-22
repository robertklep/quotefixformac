//  QuoteFixUpdaterAppDelegate.m
//  QuoteFixUpdater
//
//  Created by Robert Klep on 21-11-11.
//  Copyright 2011 Robert Klep. All rights reserved.

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
	NSLog(@"QuoteFixUpdater initializing...");
	[self startMailObserver];
    updatebundle = [bundle retain];
    relaunchpath = [path retain];
    updater = [[SUUpdater updaterForBundle:updatebundle] retain];
    [updater setDelegate:self];
    [updater resetUpdateCycle];
    return YES;
}

- (void) handleTerminateApplicationNotification:(NSNotification *) notification {
	NSDictionary 			*userInfo  	= [notification userInfo];
	NSRunningApplication	*app		= (NSRunningApplication *) [userInfo objectForKey:NSWorkspaceApplicationKey];
	NSString				*bundleid	= [app bundleIdentifier];

	if ([bundleid isEqualToString:@"com.apple.mail"])
	{
		NSLog(@"QuoteFixUpdater: Mail has quit, so we'll quit too.");
		[self quit];
	}
}

- (void) startMailObserver {
	NSLog(@"QuoteFixUpdater: starting Mail observer");
	[[[NSWorkspace sharedWorkspace] notificationCenter]
		addObserver	: self
		   selector : @selector(handleTerminateApplicationNotification:)
			   name : NSWorkspaceDidTerminateApplicationNotification
			 object : nil
	];
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
    NSLog(@"QuoteFixUpdater quiting");
    [connection invalidate];
    [NSApp terminate:self];
}

-(void) dealloc {
	[[[NSWorkspace sharedWorkspace] notificationCenter] removeObserver:self];
    [connection release];
    [updatebundle release];
    [relaunchpath release];
    [updater release];

    [super dealloc];
}

@end

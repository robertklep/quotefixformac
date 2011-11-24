//
//  main.m
//  QuoteFixUpdater
//
//  Created by Robert Klep on 21-11-11.
//  Copyright 2011 Robert Klep. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import "QuoteFixUpdaterAppDelegate.h"

int main(int argc, char *argv[])
{
    // return NSApplicationMain(argc, (const char **)argv);
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    
    [NSApplication sharedApplication];
    
    QuoteFixUpdaterAppDelegate *delegate = [[QuoteFixUpdaterAppDelegate alloc] init];
    
    [NSApp setDelegate:delegate];
    [NSApp run];
    
    [pool drain];
    return 0;
}

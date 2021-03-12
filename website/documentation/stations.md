---
id: 92
title: Stations
date: 2013-12-22T15:41:14-06:00
author: Curtis Olson
layout: page
guid: http://madesigner.flightgear.org/?page_id=92
---

MAD incorporates a concept called stations.  This is simply the
location of the ribs along the span of the wing.

For example: if you create a wing with a 30" (half) span and wanted 3"
rib spacing your stations would be:

>0, 3, 6, 9, 12, 15, 18, 21, 24, 27, and 30.

Notice this gives you 11 ribs including the root and tip ribs.  It's
as easy as that!


# Automatic Station Generation

MAD has an "Assist me" menu function to automatically generate evenly
spaced stations for your wing.  10 seconds and you are done.

# Custom Station Positions

You may not want regular spaced ribs.  Perhaps you would like to have
extra ribs near the root for additional structure.  Maybe you want to
move or add ribs to anchor the two ends of an exactly sized aileron or
flap.  It is very easy to add, remove, and move your stations (rib
positions) simply by editing the list of station locations.  For
example:

>0 1 2 4 6 9 12 15 18 20 23 26 28.5 30

This would place ribs at the above positions along the span of the
wing.  It concentrates more ribs near the root.  And perhaps you wish
a built up aileron to start at station 18 and extend to station 28.5,
so we have stations defined at those locations.

As a designer/engineer you can adjust rib positions to achieve the
structure/strength you require along with creating the spacing you
need for other structures.  It may take a little bit of thought to
make everything work out evenly, but that's half the fun of a new
design.

Notice that stations can be any whole or fractional number.  28.5 is
allowed, 14.33333 is fine too.  Use whatever decimal precision you
need to make your design work out the way you want.

Also notice that when it comes time to add other wing features, they
don't have to extend the entire span of the wing.  You can specify
starting and ending stations for any feature.  Thus you may wish to
put some thought into your exact station positions as your design
evolves.
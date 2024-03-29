---
id: 86
date: 2013-12-22T15:20:09-06:00
author: Curtis Olson
layout: page
guid: http://madesigner.flightgear.org/?page_id=86
---

## Overview and Work Flow

If you have a good idea of what you want, you can create a new wing in
MAD in a few minutes.  This includes outputting an exact 3d model so
you can take a close look at what you have asked for, what MAD has
produced, and see exactly how your design will look when it is built.
It also includes laying out all your parts on sheets ready to send to
your favorite laser cutter.

1. Start a new design
2. Input the basic design information on the "Overview" page and
   select the units you wish to use for your design.
3. Add a Wing.  (This creates a new tab next to the Overview tab.)
4. Fill in the basic information for your wing such as span, chord,
   airfoil, etc.
5. Add any features you wish including spars, stringers, leading &
   trailing edges, sheeting, lightening holes, and build tabs.
6. Save your design and build it.
7. View your results in 3d and make sure everything looks like you
   have intended it, or make refinements and rebuild your design.
8. When you are happy with the build, look in the same folder as your
   design file and you will find your plans, laser cut sheets, and
   part templates.  These are all in .svg format.  Many software
   packages can load and edit svg files, but if you don't have a
   favorite, I recommend "Inkscape" from inkscape.org.

## Interesting/Advanced Features

MAD has a number of interesting features that you might not notice at
a quick glance.  Here are a few things to keep in mind as you design
your next project:

* MAD includes a database of 1500+ airfoils.  If you can find it on
  the internet or if it's been used on a real model or real aircraft,
  it is probably in the MAD database.
* When adding a leading edge, MAD will do a "best fit" cutout of your
  airfoil rib.  This means that your post assembly sanding work to get
  back to the exact airfoil leading edge shape will be mathematically
  minimized.
* Trailing edge stick is places using a best fit algorithm as well.
  Airfoils come in all shapes and trailing edge stock will rarely
  match the original shape exactly.  MAD matches the exact trailing
  edge tip to the airfoil tip and then rotates the leading edge for a
  best fit to your airfoil.  Even so the thickness of your trailing
  edge stock may not be an exact match with the airfoil at that point.
  MAD will carefully shave or thicken the airfoil so it matches the
  trailing edge stock exactly.  This is so subtle you may not ever
  notice or think about it unless I point it out.
* Quickly add features (stringers, holes, etc.) and specify the
  starting and ending stations.  Even though MAD allows you to quickly
  design structures, it still allows the designer to make all the
  engineering decisions.
* When wing twist is asked for, MAD builds it right into the design
  for you (with optional build tabs and spar cutout alignments) so
  everything locks in and builds exactly the way you intended.
* Supports tapered wings by specifying a root chord and a tip chord.
* Want to get extra creative?  MAD allows you to enter a spline curve
  that defines the wing chord along the span.  Sound hard?  It's not
  at all, and it allows you to take your design to the next level of
  creativity.
* MAD will let you enter a sweep angle for swept wings, but doesn't
  stop there.  If you want to get extra crazy, MAD lets you enter a
  spline curve that defines the amount of sweep along your wing span.
  Why would you want to do this?  I don't know, but it's there as an
  option.
* Many real world designs use different root and tip airfoils and
  blend between them.  If you'd like to do this in your design, it's
  no problem in MAD.  Just define a tip airfoil and you are done.  MAD
  automatically blends your airfoil ribs for you.
* As I write this, control surfaces are a work in progress, but when
  the gui is ironed out, you'll be able to cut in control surfaces
  (flaps and ailerons), specify the starting and ending stations,
  hinge line location, and MAD will generate all the parts for built
  up ailerons.
* Changes are easy.  The structure of MAD means you can add and remove
  features, change sizes, locations, even make radical changes like
  picking a new airfoil, and everything is rebuilt automatically and
  consistently.  You aren't stuck redrawing every part like you might
  have to do in a typical 3d modeling tool.
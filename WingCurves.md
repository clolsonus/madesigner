# Creative Wing Curve Shapes #

Most model airplane wings have straight edges.  Many aircraft have rectangular wing shapes.  A few aircraft may have wing taper where the wing get smaller at the tip, but the leading and trailing edges are still a straight line.  Once in a while you might see a wing that is eliptical and continously curving like the Spitfire.  But what if you'd like to get more creative and design something like the stinson gull wing which sports a beautiful curve that starts narrower at the root, but then gets wider before it gets narrower again.  Read on!

# Details #

To understand how simple it is to design a wing with beautiful sweeping curves, we have to understand just a little bit about curves.  This might sound like math class, but hang in here, it's really simple stuff.  The software takes care of all the tricky hard parts.  You get to do the easy fun parts.

## Curves ##

First of all, get your brain fired up for a simple 2D X, Y plot.  Look at the following picture:  You will see a segmented green line that goes through 4 points (including the start and finish points.)  You will also see a smooth red line that goes through the same 4 points.  The red line is called a spline curve.  Imagine if you took a flexible ruler and flexed it to go through those 4 points, this is essentially the same curve as a spline.

![http://wiki.madesigner.googlecode.com/git/images/curve-demo0.png](http://wiki.madesigner.googlecode.com/git/images/curve-demo0.png)

So think about this.  If you want to create a fancy curved profile for your wing, all you have to do is pick a couple points along the path and let the software fit a nice curve for you.  You get to pick the points and tweak them until you get the curved shape you like.  That's the fun part.  Let the software crunch the math.

## Sweep ##

Wing sweep is just what you think it is.  A piper cub or your typical RC trainer has zero wing sweep.  A commercial jet liner usually has quite a bit of wing sweep.  Most designers make a straight wing, but you don't have to.  You can define a curve (probably with just 3 or 4 points at the most) and make your wing follow that curve.

## Taper ##

Taper is also very simple.  A piper cub has zero wing taper, except for the rounded wing tips, it has a rectangular wing.  Many high tech aerobatic planes like Extra's and Sukoi's have a straight, but tapered wing.  The wing is wider at the root and narrower at the tip.  Commercial jets combine quite a bit of wing taper with wing sweep.  Flying wings like a classic zagi usually have both sweep and taper.

Most designs have a constant taper, but you can define the wing chord as a curve along the length of the span.

## Example ##

The following wing has a 30 inch "half" span.  The chord is 9 inches at the root.  Five inches outwards from the root, the chord is 11 inches.  At the tip, the chord is 6 inches.  If you provide those three points as your curve, here is what you get:

![http://wiki.madesigner.googlecode.com/git/images/curved-wing1.png](http://wiki.madesigner.googlecode.com/git/images/curved-wing1.png)

# Code #

```
#!/usr/bin/env python

import svgwrite
import wing

wing = wing.Wing()

# define the wing layout
wing.units = "in"
wing.load_airfoils("naca0015")
wing.span = 30.0
wing.twist = 3
wing.set_sweep_angle(0)
wing.set_taper_curve( ((0.0, 9.0), (5.0, 11.0), (30.0, 6.0)) )

# define the wing structure
wing.steps = 20
wing.leading_edge_diamond = 0.2
wing.trailing_edge_w = 1.0
wing.trailing_edge_h = 0.25
wing.trailing_edge_shape = "symmetrical"

wing.add_stringer( side="top", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125 )
wing.add_stringer( side="bottom", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125 )
wing.add_stringer( side="top", orientation="tangent", percent=0.75, \
                       xsize=0.125, ysize=0.125 )
wing.add_stringer( side="bottom", orientation="tangent", percent=0.75, \
                       xsize=0.125, ysize=0.125 )
wing.add_spar( side="top", orientation="vertical", percent=0.30, \
                       xsize=0.125, ysize=0.250 )
wing.add_spar( side="bottom", orientation="vertical", percent=0.30, \
                       xsize=0.125, ysize=0.250 )

# build the wing parts
wing.build()

# generate building plans
wing.layout_plans( "curved-wing", 24, 36 )
```
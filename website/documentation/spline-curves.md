---
id: 95
date: 2013-12-22T15:53:15-06:00
author: Curtis Olson
layout: page
guid: http://madesigner.flightgear.org/?page_id=95
exclude: true
---

Spline curves are an integral element to MAD designs.  If your design
calls for all straight edges, then you don't need to worry about
these, but for a small bit of work, you can really liven up your
design with careful use of curves.  The Spitfire is one of WW-II's
most beautiful fighter airplanes and it didn't get this recognition
for it's straight lines.  Typically curves are hard to design and
build into model airplanes, but MAD makes it easy from start to
finish.

# What is a "spline curve"?

Spline curves were often used by ship builders to create curved hull
designs.  Imagine you place some pins at key points along your curve
outline and the fit a flexible ruler through the pins.  Conceptually
that's all there is to it.

# How do I make a "spline curve" in MAD?

It's really simple actually.  Let's go back to a simple example of a
wing with a 30" half span.  The root station is station 0.0 and the
tip station is station 30.0.

We can define a very simple two point curve (which is really a
straight line) by giving coordinate pairs in the form of (station pos,
chord)

So to create a tapered wing with a 10" root chord and a 6" tip chord
we could create the following spline curve "(0, 10) (30, 6)".  Notice
these are just pairs of numbers in parentheses.

Two points form a straight line, so that's not very interesting.
Let's make a 3-point curve.  "(0,10) (9.5,12) (30,6)" If we look at
these points carefully, you will see that at position 0 (the root rib)
we ask for a 10" chord.  9.5" out from the root we ask for a 12" rib.
Finally at position 30 (the tip) we ask for a 6" chord.  Fit a
flexibly ruler between those 3 points and that is exactly what MAD
produces.  You can do a lot with only 3 points and may never need more
than that.  Now you have a curvy sexy wing that stands out at the
field from everyone else's simple straight wing!
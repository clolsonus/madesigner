---
id: 95
title: Spline Curves
date: 2013-12-22T15:53:15-06:00
author: Curtis Olson
layout: page
guid: http://madesigner.flightgear.org/?page_id=95
---
Spline curves are an integral element to MAD designs.  If your design calls for all straight edges, then you don&#8217;t need to worry about these, but for a small bit of work, you can really liven up your design with careful use of curves.  The Spitfire is one of WW-II&#8217;s most beautiful fighter airplanes and it didn&#8217;t get this recognition for it&#8217;s straight lines.  Typically curves are hard to design and build into model airplanes, but MAD makes it easy from start to finish.

# What is a &#8220;spline curve&#8221;?

Spline curves were often used by ship builders to create curved hull designs.  Imagine you place some pins at key points along your curve outline and the fit a flexible ruler through the pins.  Conceptually that&#8217;s all there is to it.

# How do I make a &#8220;spline curve&#8221; in MAD?

It&#8217;s really simple actually.  Let&#8217;s go back to a simple example of a wing with a 30&#8243; half span.  The root station is station &#8220;0.0&#8221; and the tip station is station &#8220;30.0&#8221;.

We can define a very simple two point curve (which is really a straight line) by giving coordinate pairs in the form of (station pos, chord)

So to create a tapered wing with a 10&#8243; root chord and a 6&#8243; tip chord we could create the following spline curve &#8220;(0, 10) (30, 6)&#8221;.  Notice these are just pairs of numbers in parentheses.

Two points form a straight line, so that&#8217;s not very interesting.  Let&#8217;s make a 3-point curve.  &#8220;(0,10) (9.5,12) (30,6)&#8221;  If we look at these points carefully, you will see that at position 0 (the root rib) we ask for a 10&#8243; chord.  9.5&#8243; out from the root we ask for a 12&#8243; rib.  Finally at position 30 (the tip) we ask for a 6&#8243; chord.  Fit a flexibly ruler between those 3 points and that is exactly what MAD produces.  You can do a lot with only 3 points and may never need more than that.  Now you have a curvy sexy wing that stands out at the field from everyone else&#8217;s simple straight wing!
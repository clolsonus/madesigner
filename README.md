# MADesigner v1.0


# Project Description

The general purpose of this project is to build up a python library to
enable writing simply python scripts that generate model airplane
designs.  The initial vision includes:

- processing/blending/smoothing airfoils
- cutting out spars, stringers, sheeting, lightening holes, etc. from wing ribs
- laying out top down "plans" for the major aircraft subassemblies
- generating cut files that could be handed to a laser cutter (or cnc machine)
- generating surface "skins" that could be handed to a cnc machine for cutting
  molds
- generating 3d models for importing into flight simulators.

Hopefully this next statement will become quickly out dated, but this
is a very young project and does not have all the capabilities yet
that are listed as goals.  I decided to "publish" the project publicly
because there are a few things working that could be an interesting
curiousity or idea generator for others.


# 35,000' Overview

One of the most satisfying things in life is to create something
yourself.  From sewing to landscaping to flying a rocket to mars:
designers pour their heart and soul and creativity into clever and
interesting designs.  Even with common well known items, it is still
immensely satisfying to design and build (or even fix) it yourself.

In recent years we have made great strides in developing rapid
prototyping tools.  We have a variety of 3d design tools that have a
dizzying array of features (often even more dizzying when you start
trying to figure them out!)  Once the design is drawn up in the
computer, we now have a suite of tools from laser cutters, to CNC
routers, to 3d printers which can create the actual parts accurately
and quickly.  All that remains is to assemble the parts and your
design is finished.

More recently that has been a big push to "open source" the production
of hardware.  Others can summarize what this means better than I can,
but "open source" fabrication includes open-source designs,
open-source manufacturing machines, open-source 3d models.  There is
still a cost to physically produce a part and distrubute it, but the
goal is to apply community open-source development and improvement
techniques to part design and production.  The end goal is to lower
costs and make the whole process more accessible and more possible for
even us little guys.  We give up some concept of "ownership" of the
design and the tools to create and build it, but we gain far more in
the end.

However, one of the big stumbling blocks to this whole process is the
complexity and cost of the 3d computer design software itself.  There
can be a huge cost for advanced CAD software and also a huge learning
curve to understand the software well enough to do anything useful
with it.

MADesigner is an experiment to help address the cost and complexity of
the design portion of the process; focused primarily on the area of
model aircraft which is one of my life long interests.

It will take some time to realize all the goals I can envision for
this project, but I would like MADesigner to reduce the time to design
an entire model aircraft from scratch to just minutes.  Select an
airfoil, choose the basic layout of the model, tweak the scale and the
dimensions, and then run the scripts.  What should pop out are 3-view
drawings; nested cut files for a laser cutter or CNC machine to make
all the "hard" or "curvey" parts; full size plans; 3d cutaway models
that you can spin around and look inside of; and even an assembly
manual with practical build tips could all be fully automated.

Even though a basic "cooky cutter" design can be produced quickly, the
designer can spend time up front adjusting their aircraft, engineering
the structures, selecting materials, adjusting the lines and the
proportions, personalizing it, making engineering tradeoffs, and
ultimately making the design entirely their own.


# Capabilities

Now let's come back to earth after seeing the 35,000' view.  What are
some of the actual capabilities available right now?

- load any airfoil from the UIUC airfoil database.

- do a smooth spline interpolation (fit) of the surface points that
  wraps around the nose of the airfoil in one continuous smooth curve.

- resample the smoothed airfoil at any resolution

- simplify a higher resolution sample with an adaptive fit algorithm
  that maintains a set error tolerance with a minimal number of
  points.  This leads to smaller output files, faster cut times, while
  still maintaining as much precision as you like at any scale.

- blend two airfoils together in any proportion.  This is ideal for a
  wing panel that has one airfoil at the root and different airfoil at
  the tip.  A series of airfoils (ribs) can be generated that
  incrementally and smoothly blend from the starting airfoil to the
  ending airfoil.

- rotate an airfoil by any amount.  This allows creating a wing with
  twist or washout by incrementally rotating each rib in the plan the
  correct amount to smoothly blend in the desired washout from root to
  tip.

- scale an airfoil up or down to any size.  There's no reason a
  designer couldn't smooth and resample an airfoil at a very high
  resolution and create full scale plans for a home built aircraft.

- skin a layer off the airfoil.  This is useful if you plan to sheet
  the wing (or a portion of the wing) with sheeting of some particular
  thickness.  You can shave the exact amount off the core rib so that
  when the wing is finally sheeted, you are back to the exact
  dimensions you originally intended in your design.  You can sheet
  all or individual portions of the upper and lower curves of your
  wing.

- cut out a leading edge 'diamond' of some dimension.  Kit and scratch
  builders will know what this is all about.  It's a way to lock
  together the leading edge of the ribs, provide a starting point for
  sheeting the leading edge of the wing, and minimizes the amount of
  sanding you need to get back to the correct rounded airfoil shape.
  The diamond cutout algorithm tries to do a best fit of the diamond
  shape to the leading edge of your airfoil in order to maintain the
  original shape as close as possible while minimizing the amount of
  sanding required to finish the wing.

  In other words, for a fully symetrical airfoil (like a NACA0015) the
  square leading edge stock will be rotated exactly 45 degrees.  But
  in a flat bottom or semisymetrical airfoil, the square stock might
  be rotated 50-60 degrees for a better fit with the leading edge.

- Cut in notches for stringers and spars.  Any size notch can be cut.
  In addition, the cut out can be made relative to the top or bottom
  of the airfoil.  The cut can be vertical (which would be appropriate
  for a spar) or a the cut out can be made tangent to the wing surface
  which might be appropriate for a supporting stringer.

  You can get a bit clever/creating by combining the cut out feature
  with the airfoil rotate feature and can cut the proper washout
  alignment right into the spar notch of your airfoil.

- Add build support tabs to help align the rib correctly on your build
  surface.  This is sort of the opposite of cutting out a spar notch
  combined with carefully selecting the height of the tab.  These tabs
  are removed once the basic wing structure is framed together.
  Again, model airplane builders will know exactly what this feature
  is and why it's useful.  Planes fly much better with accurately
  built wings that are straight and true.

- Cut lightening holes into the ribs.  Good for adding lightness to
  your design.  Also good for precutting holes for wing alignment jigs
  or wing joiner tubes.

- (TODO) better support of custom part labels (the text and the position)


# Road Map

This is a hobby project in my spare time so I am trying to measure my
efforts and balance good forward progress with feature complete
design.  My design process is "iterative" and based on trying to push
a couple real world examples through from start to finish.  When I run
up against something I missed I will cycle back and add that feature
and push it downstream through the whole process.  Hopefully
eventually arriving at a useable system that doesn't do everything for
everyone, but does a lot from start to finish.

Initially I have made good progress on basic airfoil manipulation and
cutting out notches and holes required for real world construction.

Next up I will look at laying out the wing plan from the top down and
drawing the wing from the front/side view.  I would like to be able to
output full size plan sheets for those with a plotter big enough to
handle them.

Also, it is important to me to be able to lay out all the individual
parts onto part sheets so they can be cut out by a laser cutter or cnc
router.  That is the key to this whole project -- not only designing
the plans, but doing it in a way that the parts can be quickly and
accurately produced, and then easily assembled.

Also on my radar screen is applying all these core capabilities to
fuselage design and construction.  The shapes are different between a
wing and a fuselage, but much of the process is analogous.


# Frequently Asked Questions

Here's a quick FAQ (although no one has yet asked me any questions, so
I'm just trying to anticipate what people might be thinking.)

Q: So why write python scripts to generate model aircraft designs?

Scripted design is a different mind set.  Consider that if the scripts
are setup well and I want to make a small tweak (like increase the
wing chord size by a 1/2 inch, or try a slightly different airfoil),
then in my script it is a small tweak, I rerun the script and out pops
all the new cut files and new plans.  If I wanted to make this change
in a traditional cad program I might have to spend all evening making
the same small change to a bazillion parts since everything is linked
together and these small tweaks tend to have a large cascading effect.
But you do give up the ability to visually manipulate the design.
However, you can quickly run the script and view the output, so there
is some visual feedback in the process.

Another reason is when you run up against the limit of what a tool
like "profili" is able to offer you through it's gui interface, then
what do you do?  (a) do you live within the constraints of the gui?
(b) use a scripting system that lets you steer off the roads and do
your own clever/crazy things?


Q: Still that sounds like a lot of effort for something no one else will 
probably ever use.

Yes again, but this is project is a nice mental break from my daily
grind.  I'm having fun and teaching myself python at the same time.
And besides, I always wanted to be an aerospace engineer when I grew
up.


Q: Can your python design scripts do "xyz"

Yes it's python so you can add "xyz" feature yourself!  Ok, but more
seriously I am building up a core collection of basic design and
assembly features.  This is for fun so I'm not really taking requests,
but if it's an easy thing to add or something that sounds interesting
to tackle, I might be interested.


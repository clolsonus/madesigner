# Wing Plan Layout #

By specifying some basic wing layout parameters along with the core structural
components of the wing, not only can the rib shapes be drawn with all the
appropriate notches and cutouts, but the top down wing plan can be laid out
in life size so the wing can be assembled on top of the plan.  This helps
ensure everything goes together exactly right.


# Details #

The following image shows an example wing plan.  This plan was automatically
generated using the script attached below.  Not only does this script generate
a life size wing building plan, but it also generates all the rib cutout
sheets to send to a laser printer as well as rib templates you can print on
your own printer and cutout.

In the following plan please notice:
  * The leading edge 'diamond' stock is drawn as if it has been sanded down to the ideal airfoil shape.  Because this is a tapered wing with varying size ribs, the shape changes subtlely from root to tip.
  * Stringers and spars are drawn correctly.
  * The wing ribs are labelled correctly.
  * Trailing edge stock is drawn in (but ailerons and flaps are not yet accounted for.)
  * The root and tip ribs are nudge inwards a bit t line up with the ends of the stringers and yield a wing that is the exact span specified in the script.

![http://wiki.madesigner.googlecode.com/git/images/sport-flyer-wing.png](http://wiki.madesigner.googlecode.com/git/images/sport-flyer-wing.png)

# Code #

```
#!/usr/bin/env python

import wing

# define the wing layout
wing = wing.Wing()
wing.units = "in"
wing.load_airfoils("naca0015")
wing.root_chord = 10.0
wing.tip_chord = 6
wing.span = 30.0
wing.twist = 3
wing.sweep = 0

# define the wing structure
wing.steps = 10
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

# create the cut sheet layouts
wing.layout_parts_sheets( "sport-flyer", 24, 4 )

# create the template layouts
wing.layout_parts_templates( "sport-flyer", 8.5, 11 )

# generate the plans
wing.layout_plans( "sport-flyer", 24, 36 )
```
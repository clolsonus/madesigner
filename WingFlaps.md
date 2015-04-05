# Built-up Control Surfaces #

One of the trickier aspects of model aircraft design is engineering
the control surfaces.  In a simple straight wing, you may wish to just
cut off the trailing edge of the wing and used preshaped aileron
stock.  Many many model airplane kits do exactly this.

But what about more complicated wings with 'barn door' type ailerons.
These are built up and need to follow the overall layout of the wing
very carefully and precisely.  In a complex tapered or curved or
elliptical wing, this can be very tricky to engineer.

Madesigner does most of the difficult work for.  You still have to
design/engineer the overall shape of the wing and the size and proportion of the
control surfaces.  You still have to engineer sufficient structure and
make sure there aren't any design conflicts (like trying to cut a
control surface through a main structural spar.)  Generally any design
will need close review at the end with some followup tweaks to make
everything work well together.

# Details #

Adding a control surface to a wing is as simple as a single function
call with a few parameters.

```
wing.add_flap( start_station=17.0, end_station=28.0, \
                   pos=ailpos, type="builtup", angle=30.0, \
                   edge_stringer_size=edge_stringer_size )
```

This adds a control surface to both right and left wings.

# Stations #

Wing ribs are located at "stations" along the span of a wing.  You can
define the actual station locations if you wish, or you can simply
define how many ribs you'd like and the code will space the stations
evenly across the span of the wing.

Stations are referred to by their distance from the root rib.  In the
above exampe we specify a control surface that spans station 17.0 to
station 28.0.  This design uses inches as the units so this is an 11
inch wide built up control surface.

# Hinge Line #

A very important aspect of built up control surfaces is the
requirement to have a straight hinge line.  (Think about it, curved
hinges do not work very well!)  The 'pos' parameter allows you to
define the front/back position of the start of the cutout (i.e. the
hinge line.)  You can specify a position that is some distance behind
the leading edge, some distance forward of the trailing edge, or at a
percentage point of the chord.

But what about wings (like this example) where following any of these
positions would lead to a curved hinge?  In addition to the above
positioning methods, you can also specify the position at the inner
station + a slope of the cutout, so you can put your hinge anywhere
you like in the wing and have it follow any angle line you like.

# Wedge Cutout #

The design/engineering approach to the control surfaces is to place
the hinge point at the top line of the wing.  The intension is to then
join the moveable control surface to the wing using a gapless hinge
scheme.  Gapless hinges are becoming much more popular and are quite
easy to attach and are quite robust when all the parts are engineered
with this scheme in mind.

You can specify the cutout/wedge angle (i.e. 30 degrees) and this then
defines the maximum downward deflection the surface can achieve.

Also notice that the main rib at the boundary of the control surface is shifted over by 1/2 the rib width and the matching control surface partial rib is shifted by 1/2 rib width in the opposing direction.  This makes everything fit and allows you to sheet or cover the entire cutout surface.

# Boundary Stringers #

The code automatically places boundary stringers at the hinge edges
(both top and bottom) so you as the builder have some structure to
attach your covering and hinge to (or to support sheeting if you are
building a fully or partially sheeted wing.)  Because with a gapless
hinge, the hinge load is spread across the entire length of the
surface, we can use much lighter materials around the hinge line and
don't need big blocks of balsa to anchor point hinges into.  This
saves on building, sanding, and weight, while allowing you to construct
complicated shapes with minimal sanding and use off the shelf stock
materials.

You may notice in the example wing that the top and bottom stringers for the control surface are not exactly parallel.  This is because we are cutting a fixed angle wedge out of a wing that has varying thickness. This means the control surface thickness changes along the span and the bottom line of the wedge cutout is not parallel to the top.

This is all computed and handled inside the code so you don't have to worry about it, but it's good to be aware and understand a bit of what is happenging under the hood.

## Example ##

The following wing has a curved taper.  It starts out narrower, gets wider about 1/3rd of the out and then comes back to being narrower at the tip.  I have specified 2 control surfaces, one will be a traditional flap and one will be a traditional aileron.  These are mirrored automatically between left & right wings.

![http://wiki.madesigner.googlecode.com/git/images/curved-wing2.png](http://wiki.madesigner.googlecode.com/git/images/curved-wing2.png)

# Code #

```
#!/usr/bin/env python

import contour
import wing

wing = wing.Wing()

# define the wing layout
wing.units = "in"
wing.load_airfoils("naca0015")
wing.span = 30.0
wing.twist = 0
wing.set_sweep_angle(0)
root_chord = 9.0
tip_chord = 6.0
wing.set_taper_curve( ((0.0, root_chord), (5.0, root_chord*1.2), (30.0, tip_chord)) )

# define the wing structure
wing.set_stations( (0.0, 1.0, 2.0, 4.0, 7.0, 10.0, 13.0, 15.0, 17.0, \
                        20.0, 23.0, 26.0, 28.0, 29.0, 30.0) )
wing.leading_edge_diamond = 0.2

wing.add_trailing_edge( width=1.0, height=0.25, shape="symmetrical", \
                            start_station=0.0, end_station=1.0, part="wing" )
wing.add_trailing_edge( width=1.0, height=0.25, shape="symmetrical", \
                            start_station=15.0, end_station=17.0, part="wing" )
wing.add_trailing_edge( width=1.0, height=0.25, shape="symmetrical", \
                            start_station=28.0, end_station=30.0, part="wing" )

wing.add_spar( side="top", orientation="vertical", xpos=0.0, \
                   xsize=0.125, ysize=0.250, part="wing" )
wing.add_spar( side="bottom", orientation="vertical", xpos=0.0, \
                   xsize=0.125, ysize=0.250, part="wing" )

wing.add_spar( side="top", orientation="vertical", xpos=4.0, \
                   xsize=0.125, ysize=0.250, part="wing", \
                   start_station=0.0, end_station=17.0 )
wing.add_spar( side="bottom", orientation="vertical", xpos=4.0, \
                   xsize=0.125, ysize=0.250, part="wing", \
                   start_station=0.0, end_station=17.0 )

wing.add_stringer( side="top", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125, part="wing" )
wing.add_stringer( side="bottom", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125, part="wing" )
wing.add_stringer( side="top", orientation="tangent", percent=0.50, \
                       xsize=0.125, ysize=0.125, \
                       start_station=10.0, end_station=30.0, part="wing" )
wing.add_stringer( side="bottom", orientation="tangent", percent=0.50, \
                       xsize=0.125, ysize=0.125, \
                       start_station=10.0, end_station=30.0, part="wing" )

# define the control surfaces
ailpos = contour.Cutpos(xpos=4.0, atstation=17.0, slope=-0.1)
edge_stringer_size = ( 0.250, 0.125 ) # width x height
wing.add_flap( start_station=17.0, end_station=28.0, \
                   pos=ailpos, type="builtup", angle=30.0, \
                   edge_stringer_size=edge_stringer_size )
wing.add_trailing_edge( width=1.0, height=0.25, shape="symmetrical", \
                            start_station=17.0, end_station=28.0, part="flap" )

flappos = contour.Cutpos(xpos=4.5, atstation=1.0, slope=0.05)
wing.add_flap( start_station=1.0, end_station=15.0, \
                   pos=flappos, type="builtup", angle=45.0, \
                   edge_stringer_size=edge_stringer_size )
wing.add_trailing_edge( width=1.0, height=0.25, shape="symmetrical", \
                            start_station=1.0, end_station=15.0, part="flap" )

# build the wing parts
wing.build()

# create lasercut sheets
wing.layout_parts_sheets( "sport-flyer", 24, 8 )

# create paper templates
wing.layout_parts_templates( "sport-flyer", 8.5, 11 )

# generate building plans
wing.layout_plans( "sport-flyer", 24, 36 )
```
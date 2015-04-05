# Airfoil Cutouts #

In addition to basic airfoil shape manipulation, there are functions to
cut out basic modeling construction features.


# Details #

The following figure shows cutting out a leading edge "diamond".  Notice that it is positioned for a best fit to the airfoil shape to best maintain the original nose curvature with minimal sanding.  All or a portion of either the upper or lower surface can be skinned for sheeting.  Vertical spars can be cutout.  Notice that the spars can be cut out before (or after) rotating the rib for washout, so it's possible to help build the washout right into the spar cutout.  Notice that stringers can be cut in flush with the upper or lower surface and can be either tangent to the surface or vertical.  Finally, any number of build tabs can be added at any position in the rib.  Front and rear tabs could be added to lift the entire rib off the surface if that is appropriate for a particular wing design (perhaps a highly tapered design.)

A recent addition is 'shaped' lightening holes that follow the
interior contour of the rib and have rounded corners.  These are
created with a single function call the specifies the start and ending
point of the cutout, how much material to save on the top and bottom,
and then the size of the corner radius.

Also shown (but it's very subtle) is a 'best fit' of the trailing edge stock that matches the exact tip of the airfoil and then fits the stock (either flat or symmetric cross section) as best as possible to the airfoil.  Also available as an option is to subtle shave the last 2/3 of the airfoil surface to exactly match the stock trailing edge height.

![http://wiki.madesigner.googlecode.com/git/images/demo-cutouts0.png](http://wiki.madesigner.googlecode.com/git/images/demo-cutouts0.png)

# Code #

```
#!/usr/bin/env python

import copy
import svgwrite
import airfoil
import contour
import layout

rchord = 8.0
tchord = 5.0
twist = 0

width = 8.5
height = 11

print "coutouts demo"
layout = layout.Layout( 'demo-cutouts', width, height )

root = airfoil.Airfoil("naca633618", 1000, True)
tip = airfoil.Airfoil("naca0015", 1000, True);

steps = 8
dp = 1.0 / steps

for p in range(0, steps+1):
    print "Making rib " + str(p)
    percent = p*dp

    blend = airfoil.blend( root, tip, percent )
    blend.fit( 500, 0.0001 )
    size = rchord * (1.0 - percent) + tchord * percent
    blend.scale( size, size )
    blend.move(-size / 3.0, 0)

    # do this before any other cuts if "force_fit" is True because it
    # can change the base airfoil a bit to match the trailing edge
    # stock.
    blend.cutout_trailing_edge( 1.0, 0.25, shape="symmetrical", force_fit=True )

    bounds = blend.get_bounds()

    # leading edge diamond (before washout rotate)
    blend.cutout_leading_edge_diamond( 0.200 )

    # sheet whole wing
    blend.cutout_sweep( side="top", xstart=bounds[0][0], xdist=size*2, ysize=0.0625 )
    blend.cutout_sweep( side="bottom", xstart=bounds[0][0], xdist=size*2, ysize=0.0625 )

    # stringer position tapers with wing (if there is a taper)
    cutpos = contour.Cutpos( percent=0.15 )
    cutout = contour.Cutout( side="top", orientation="tangent", cutpos=cutpos, \
                                 xsize=0.125, ysize=0.125 )
    blend.cutout_stringer( cutout )

    # stringer position fixed relative to nose of rib
    cutpos = contour.Cutpos( front=0.25 )
    cutout = contour.Cutout( side="top", orientation="tangent", cutpos=cutpos, \
                                 xsize=0.125, ysize=0.125 )
    blend.cutout_stringer( cutout )

    # rear stringer (before washout rotate)
    cutpos = contour.Cutpos( percent=0.7 )
    cutout = contour.Cutout( side="top", orientation="tangent", cutpos=cutpos, \
                                 xsize=0.125, ysize=0.125 )
    blend.cutout_stringer( cutout )
    cutout = contour.Cutout( side="bottom", orientation="tangent", \
                                 cutpos=cutpos, \
                                 xsize=0.125, ysize=0.125 )
    blend.cutout_stringer( cutout )

    # shaped lightening holes
    start = contour.Cutpos( percent=0.07 )
    end = contour.Cutpos( percent=0.14 )
    blend.carve_shaped_hole( pos1=start, pos2=end, \
                                 material_width=0.20, radius=0.075 )
    start = contour.Cutpos( percent=0.18 )
    end = contour.Cutpos( percent=0.30 )
    blend.carve_shaped_hole( pos1=start, pos2=end, \
                                 material_width=0.20, radius=0.075 )
    start = contour.Cutpos( percent=0.36 )
    end = contour.Cutpos( percent=0.48 )
    blend.carve_shaped_hole( pos1=start, pos2=end, \
                                 material_width=0.20, radius=0.075 )
    start = contour.Cutpos( percent=0.50 )
    end = contour.Cutpos( percent=0.64 )
    blend.carve_shaped_hole( pos1=start, pos2=end, \
                                 material_width=0.20, radius=0.075 )

    # rotate entire part for twist/washout
    blend.rotate( percent * twist )

    # main spars
    cutpos = contour.Cutpos( percent=0.33 )
    cutout = contour.Cutout( side="top", orientation="vertical", \
                                 cutpos=cutpos, \
                                 xsize=0.125, ysize=0.20 )
    blend.cutout_stringer( cutout )
    cutout = contour.Cutout( side="bottom", orientation="vertical", \
                                 cutpos=cutpos, \
                                 xsize=0.125, ysize=0.30 )
    blend.cutout_stringer( cutout )

    layout.draw_part_demo( blend )

layout.save()
```
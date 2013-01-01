#!/usr/bin/env python

import copy
import svgwrite

try:
    import airfoil
    import layout
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import airfoil
    import layout

rchord = 8.0
tchord = 5.0
twist = -10

width_in = 8.5
height_in = 11
dpi = 90

print "coutouts demo"
layout = layout.Layout( 'demo-cutouts.svg', width_in, height_in, dpi )
ypos = 0.1

root = airfoil.Airfoil("naca633618", 1000, True)
tip = airfoil.Airfoil("naca0015", 1000, True);

steps = 8
dp = 1.0 / steps
ypos = 0.1
for p in range(0, steps+1):
    print p
    percent = 1 - p*dp

    blend = airfoil.blend( root, tip, percent )
    blend.fit( 500, 0.0001 )
    size = rchord * percent + tchord * (1.0 - percent)
    blend.scale( size, size )
    blend.move(-size / 3.0, 0)

    bounds = blend.get_bounds()

    # leading edge diamond (before washout rotate)
    print "cutout leading edge"
    blend.cutout_leading_edge_diamond( 0.200 )

    # leading edge sheeting (before washout rotate)
    le = bounds[0][0] + 0.125
    d = size * 0.2
    #blend.cutout_sweep( "top", le, d, 0.0625, 0.05 )
    #blend.cutout_sweep( "bottom", le, d, 0.0625, 0.05 )

    # front stringers (before washout rotate)
    fs = bounds[0][0] + size*0.1
    blend.cutout_stringer( "top", "tangent", fs, 0.125, 0.125 )
    fs = bounds[0][0] + size*0.2
    blend.cutout_stringer( "top", "tangent", fs, 0.125, 0.125 )

    # rear stringer (before washout rotate)
    rs = bounds[1][0] - tchord*0.5
    blend.cutout_stringer( "top", "vertical", rs, 0.125, 0.125 )
    blend.cutout_stringer( "bottom", "vertical", rs, 0.125, 0.125 )

    #blend.rotate( (1 - percent) * twist )

    # main spars
    blend.cutout_stringer( "top", "vertical", 0, 0.125, 0.20 )
    blend.cutout_stringer( "bottom", "vertical", 0, 0.125, 0.30 )

    bounds = blend.get_bounds()

    layout.draw_airfoil_demo( blend, width_in*0.5, ypos )

    dy = bounds[1][1] - bounds[0][1]
    ypos += dy + 0.1

layout.save()

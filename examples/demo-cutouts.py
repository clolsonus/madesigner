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
twist = -5

width_in = 8.5
height_in = 11
margin_in = 0.1
dpi = 90

print "coutouts demo"
layout = layout.Layout( 'demo-cutouts', width_in, height_in, margin_in, dpi )

root = airfoil.Airfoil("naca633618", 1000, True)
tip = airfoil.Airfoil("naca0015", 1000, True);

steps = 8
dp = 1.0 / steps

for p in range(0, steps+1):
    print p
    percent = p*dp

    blend = airfoil.blend( root, tip, percent )
    blend.fit( 500, 0.0001 )
    size = rchord * (1.0 - percent) + tchord * percent
    blend.scale( size, size )
    blend.move(-size / 3.0, 0)

    bounds = blend.get_bounds()

    # leading edge diamond (before washout rotate)
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
    rs = bounds[1][0] - size*0.3
    blend.cutout_stringer( "top", "tangent", rs, 0.125, 0.125 )
    blend.cutout_stringer( "bottom", "tangent", rs, 0.125, 0.125 )

    # lightening holes
    hx = bounds[0][0] + size * 0.16
    ty = blend.simple_interp(blend.top, hx)
    by = blend.simple_interp(blend.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.5
    blend.add_hole( hx, hy, hr)

    hx = bounds[0][0] + size * 0.44
    ty = blend.simple_interp(blend.top, hx)
    by = blend.simple_interp(blend.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.7
    blend.add_hole( hx, hy, hr)

    hx = bounds[0][0] + size * 0.57
    ty = blend.simple_interp(blend.top, hx)
    by = blend.simple_interp(blend.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.6
    blend.add_hole( hx, hy, hr)

    # rotate entire part for twist/washout
    blend.rotate( percent * twist )

    # main spars
    blend.cutout_stringer( "top", "vertical", 0, 0.125, 0.20 )
    blend.cutout_stringer( "bottom", "vertical", 0, 0.125, 0.30 )

    # build alignment tabs
    at = bounds[1][0] - size * 0.15
    blend.add_build_tab("bottom", at, 0.4 )

    at = bounds[0][0] + size * 0.15
    blend.add_build_tab("bottom", at, 0.4 )

    # label
    at = bounds[0][0] + size * 0.27
    ty = blend.simple_interp(blend.top, at)
    by = blend.simple_interp(blend.bottom, at)
    vd = (ty - by)
    hy = by + vd / 2.0
    blend.add_label( at, hy, 14, 0, "W" + str(p) )

    layout.draw_airfoil_demo( blend )

layout.save_all()

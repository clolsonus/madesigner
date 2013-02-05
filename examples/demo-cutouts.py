#!/usr/bin/env python

import copy

try:
    import svgwrite
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/..'))
    import svgwrite

try:
    import airfoil
    import contour
    import layout
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import airfoil
    import contour
    import layout

rchord = 8.0
tchord = 5.0
twist = 5

width = 8.5
height = 11

print "coutouts demo"
layout = layout.Layout( 'demo-cutouts', width, height )

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

    # do this before any other cuts if "force_fit" is True because it
    #can change the base airfoil a bit to match the trailing edge
    #stock.
    blend.cutout_trailing_edge( 1.0, 0.25, shape="symmetrical", force_fit=True )
    #blend.cutout_trailing_edge( 1.0, 0.25, shape="flat", force_fit=True )

    bounds = blend.get_bounds()

    # leading edge diamond (before washout rotate)
    blend.cutout_leading_edge_diamond( 0.200 )

    # leading edge sheeting (before washout rotate)
    le = bounds[0][0] + 0.125
    d = size * 0.2
    #blend.cutout_sweep( "top", le, d, 0.0625, 0.05 )
    #blend.cutout_sweep( "bottom", le, d, 0.0625, 0.05 )

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

    # lightening holes
    hx = bounds[0][0] + size * 0.16
    ty = blend.simple_interp(blend.top, hx)
    by = blend.simple_interp(blend.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.5
    blend.cut_hole( hx, hy, hr)

    hx = bounds[0][0] + size * 0.44
    ty = blend.simple_interp(blend.top, hx)
    by = blend.simple_interp(blend.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.7
    blend.cut_hole( hx, hy, hr)

    hx = bounds[0][0] + size * 0.73
    ty = blend.simple_interp(blend.top, hx)
    by = blend.simple_interp(blend.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.6
    blend.cut_hole( hx, hy, hr)

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

    # build alignment tabs
    pos = contour.Cutpos( percent=0.15 )
    blend.add_build_tab(side="bottom", cutpos=pos, xsize=0.4 )
    #pos = contour.Cutpos( percent=0.85 )
    #blend.add_build_tab(side="bottom", cutpos=pos, xsize=0.4 )

    # label
    at = bounds[0][0] + size * 0.27
    ty = blend.simple_interp(blend.top, at)
    by = blend.simple_interp(blend.bottom, at)
    vd = (ty - by)
    hy = by + vd / 2.0
    ##blend.add_label( at, hy, 14, 0, "W" + str(p) )

    layout.draw_part_demo( blend )

layout.save()

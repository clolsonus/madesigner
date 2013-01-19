#!/usr/bin/env python

import svgwrite

try:
    import wing
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import wing

wing = wing.Wing()

# define the wing layout
wing.units = "in"
wing.load_airfoils("naca0015")
wing.span = 30.0
wing.twist = 3
wing.set_sweep_angle(0)
#wing.set_sweep_curve( ((0.0,0.0), (15.0, -1.0), (30.0, 0.0)) )
#wing.set_chord( 10.0, 6.0 )
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

# create lasercut sheets
wing.layout_parts_sheets( "sport-flyer", 24, 4 )

# create paper templates
wing.layout_parts_templates( "sport-flyer", 8.5, 11 )

# generate building plans
wing.layout_plans( "sport-flyer", 24, 36 )

if False:
    # leading edge sheeting (before washout rotate)
    le = bounds[0][0] + 0.120
    d = chord * 0.3
    rib.cutout_sweep( "top", bounds[0][0], 12, 0.0625 )
    rib.cutout_sweep( "bottom", bounds[0][0], 12, 0.0625 )
    #rib.cutout_sweep( "top", le, d, 0.0625, 0.05 )
    #rib.cutout_sweep( "bottom", le, d, 0.0625, 0.05 )

    # lightening (or wing jig) holes
    hx = -chord * 0.1
    ty = rib.simple_interp(rib.top, hx)
    by = rib.simple_interp(rib.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.7
    rib.add_hole( hx, hy, hr)

    hx = chord * 0.1
    ty = rib.simple_interp(rib.top, hx)
    by = rib.simple_interp(rib.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.7
    rib.add_hole( hx, hy, hr)

    hx = chord * 0.3
    ty = rib.simple_interp(rib.top, hx)
    by = rib.simple_interp(rib.bottom, hx)
    vd = (ty - by)
    hy = by + vd / 2.0
    hr = (vd / 2.0)  * 0.7
    rib.add_hole( hx, hy, hr)


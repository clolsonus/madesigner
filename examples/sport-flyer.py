#!/usr/bin/env python

import svgwrite

try:
    import wing
    import airfoil
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import wing
    import airfoil

# define the wing layout
wing = wing.Wing()
wing.units = "in"
wing.load_airfoils("naca0015")
wing.root_chord = 10.0
wing.tip_chord = 5
wing.span = 30.0
wing.twist = 5
wing.sweep = 0

# define the wing structure
wing.steps = 10

# build the wing parts
wing.build()

# create the cut sheet layout
wing.layout_parts_sheets( "sport-flyer", 24, 4 )

# create the cut sheet layout
wing.layout_parts_templates( "sport-flyer", 8.5, 11 )

# generate the plans
wing.layout_plans( "sport-flyer", 24, 36 )

if False:
    # leading edge sheeting (before washout rotate)
    le = bounds[0][0] + 0.120
    d = chord * 0.3
    rib.cutout_sweep( "top", bounds[0][0], 12, 0.0625 )
    rib.cutout_sweep( "bottom", bounds[0][0], 12, 0.0625 )
    #rib.cutout_sweep( "top", le, d, 0.0625, 0.05 )
    #rib.cutout_sweep( "bottom", le, d, 0.0625, 0.05 )

    rib.cutout_leading_edge_diamond( 0.250 - 0.0625 )

    # rear stringer (before washout rotate)
    rs = bounds[1][0] - chord*0.5
    fs = -chord * 0.2
    rib.cutout_stringer( "top", "tangent", rs, 0.125, 0.125 )
    rib.cutout_stringer( "bottom", "tangent", rs, 0.125, 0.125 )
    rib.cutout_stringer( "top", "tangent", fs, 0.125, 0.125 )
    rib.cutout_stringer( "bottom", "tangent", fs, 0.125, 0.125 )

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

    #rib.rotate( (1 - percent) * twist )

    # main spars
    rib.cutout_stringer( "top", "vertical", 0, 0.250, 0.250 )
    rib.cutout_stringer( "bottom", "vertical", 0, 0.250, 0.250 )

    # label at 0 pt
    ty = rib.simple_interp(rib.top, 0.0)
    by = rib.simple_interp(rib.bottom, 0.0)
    vd = (ty - by)
    hy = by + vd / 2.0
    rib.add_label( 0.0, hy, 14, 0, "W1" )

    rib.rotate(-10)

    # build alignment tabs
    at = bounds[1][0] - chord * 0.2
    rib.add_build_tab("bottom", at, 0.5, 0.25 )
    rib.add_build_tab("bottom", fs-0.5, 0.5 )
    rib.add_build_tab("top", fs-0.5, 0.3, 0.25 )

    draw_airfoil_svg( dwg, rib, width_in*0.5, 0, True, True )

    dwg.save()

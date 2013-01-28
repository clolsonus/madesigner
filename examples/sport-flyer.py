#!/usr/bin/env python


try:
    import contour
    import wing
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import contour
    import wing

try:
    import svgwrite
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/..'))
    import svgwrite

wing = wing.Wing()

# define the wing layout
wing.units = "in"
wing.load_airfoils("naca0015")
wing.span = 30.0
wing.twist = 3
wing.set_sweep_angle(0)
#wing.set_sweep_curve( ((0.0,0.0), (15.0, -1.0), (30.0, 0.0)) )
root_chord = 9.0
tip_chord = 6.0
#wing.set_chord( root_chord, tip_chord )
wing.set_taper_curve( ((0.0, root_chord), (5.0, root_chord*1.2), (30.0, tip_chord)) )

# define the wing structure
#wing.set_num_stations(20)
wing.set_stations( (0.0, 1.0, 2.0, 4.0, 7.0, 10.0, 13.0, 15.0, 17.0, \
                        20.0, 23.0, 26.0, 28.0, 29.0, 30.0) )
wing.leading_edge_diamond = 0.2

wing.add_trailing_edge( width=1.0, height=0.25, shape="symmetrical", \
                            start_station=0.0, end_station=20.0 )
wing.add_trailing_edge( width=1.0, height=0.25, shape="symmetrical", \
                            start_station=29.0, end_station=30.0 )

wing.add_spar( side="top", orientation="vertical", center=0.0, \
                       xsize=0.125, ysize=0.250 )
wing.add_spar( side="bottom", orientation="vertical", center=0.0, \
                       xsize=0.125, ysize=0.250 )

wing.add_stringer( side="top", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125 )
wing.add_stringer( side="bottom", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125 )
wing.add_stringer( side="top", orientation="tangent", percent=0.70, \
                       xsize=0.125, ysize=0.125, \
                       start_station=0.0, end_station=20.0 )
wing.add_stringer( side="bottom", orientation="tangent", percent=0.70, \
                       xsize=0.125, ysize=0.125, \
                       start_station=0.0, end_station=20.0 )
#wing.add_stringer( side="top", orientation="tangent", percent=0.50, \
#                       xsize=0.125, ysize=0.125, \
#                       start_station=15.0, end_station=28.0 )
#wing.add_stringer( side="top", orientation="tangent", center=3.0, \
#                   xsize=0.125, ysize=0.125 )
#wing.add_stringer( side="bottom", orientation="tangent", center=3.0, \
#                   xsize=0.125, ysize=0.125 )

# define the control surfaces
pos = contour.Cutpos(center=3.0)
edge_stringer_size = ( 0.25, 0.125 ) # width x height
wing.add_flap( start_station=20.0, end_station=29.0, \
                   pos=pos, type="builtup", edge_stringer_size=edge_stringer_size )

# build the wing parts
wing.build()

# create lasercut sheets
wing.layout_parts_sheets( "sport-flyer", 24, 8 )

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


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
wing.twist = 0
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

wing.add_leading_edge( size=0.25, part="wing" )
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
#wing.add_stringer( side="top", orientation="tangent", percent=0.50, \
#                       xsize=0.125, ysize=0.125, \
#                       start_station=15.0, end_station=28.0 )
#wing.add_stringer( side="top", orientation="tangent", xpos=3.0, \
#                   xsize=0.125, ysize=0.125 )
#wing.add_stringer( side="bottom", orientation="tangent", xpos=3.0, \
#                   xsize=0.125, ysize=0.125 )

# simple round hole
pos=contour.Cutpos(xpos=-0.75)
wing.add_simple_hole( radius=0.325, pos1=pos, part="wing" )

# shaped lightening holes
start = contour.Cutpos( percent=0.35 )
end = contour.Cutpos( percent=0.55 )
wing.add_shaped_hole( pos1=start, pos2=end, \
                          material_width=0.2, radius=0.1, part="wing" )

# define the control surfaces
ailpos = contour.Cutpos(xpos=4.0, atstation=17.0, slope=-0.1)
edge_stringer_size = ( 0.250, 0.125 ) # width x height
#edge_stringer_size = None
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

wing.build_ac3d( "sport-flyer" )

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


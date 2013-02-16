#!/usr/bin/env python


try:
    import ac3d
    import contour
    import wing
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import ac3d
    import contour
    import wing

try:
    import svgwrite
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/..'))
    import svgwrite

# inner wing panels
wing1 = wing.Wing("ukulalela-wing1")

# layout
wing1.units = "in"
wing1.load_airfoils("mh43")      # http://www.mh-aerotools.de/airfoils/
wing1.span = 35.0
wing1.set_stations( (0.0, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, \
                         16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, \
                         32.0, 34.0, 35.0) )
wing1.twist = 0
wing1.set_sweep_angle(0)
wing1.set_chord( 10.0 )

# structure
wing1.add_leading_edge( size=(3.0/32.0), part="wing" )
wing1.add_trailing_edge( width=0.75, height=0.125, shape="flat", part="wing" )
wing1.add_spar( side="top", orientation="vertical", xpos=0.0, \
                   xsize=0.125, ysize=0.250, part="wing" )
wing1.add_spar( side="bottom", orientation="vertical", xpos=0.0, \
                   xsize=0.125, ysize=0.250, part="wing" )
wing1.add_spar( side="top", orientation="vertical", percent=0.60, \
                   xsize=0.125, ysize=0.125, part="wing" )
wing1.add_spar( side="bottom", orientation="vertical", percent=0.60, \
                   xsize=0.125, ysize=0.125, part="wing" )
wing1.add_stringer( side="top", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125, part="wing" )
wing1.add_stringer( side="bottom", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125, part="wing" )

wing1.build()                           # build the wing parts
wing1.layout_parts_sheets( 24, 8 )      # create lasercut sheets
wing1.layout_parts_templates( 8.5, 11 ) # create paper templates
wing1.layout_plans( 24, 36 )            # generate building plans

# outer wing panels
wing2 = wing.Wing("ukulalela-wing2")

# layout
wing2.units = "in"
wing2.load_airfoils("mh43")      # http://www.mh-aerotools.de/airfoils/
wing2.span = 21.0
wing2.set_stations( (35.0, 36.0, 38.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, \
                        52.0, 54.0, 55.0, 56.0) )
wing2.twist = 0
wing2.set_sweep_angle(0)
wing2.set_chord( 10.0, 6.0 )

# structure
wing2.add_leading_edge( size=(3.0/32.0), part="wing" )
wing2.add_trailing_edge( width=0.75, height=0.125, shape="flat", part="wing" )
wing2.add_spar( side="top", orientation="vertical", xpos=0.0, \
                   xsize=0.125, ysize=0.250, part="wing" )
wing2.add_spar( side="bottom", orientation="vertical", xpos=0.0, \
                   xsize=0.125, ysize=0.250, part="wing" )
wing2.add_spar( side="top", orientation="vertical", percent=0.60, \
                   xsize=0.125, ysize=0.125, part="wing" )
wing2.add_spar( side="bottom", orientation="vertical", percent=0.60, \
                   xsize=0.125, ysize=0.125, part="wing" )
wing2.add_stringer( side="top", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125, part="wing" )
wing2.add_stringer( side="bottom", orientation="tangent", percent=0.10, \
                       xsize=0.125, ysize=0.125, part="wing" )

wing2.build()                           # build the wing parts
wing2.layout_parts_sheets( 24, 8 )      # create lasercut sheets
wing2.layout_parts_templates( 8.5, 11 ) # create paper templates
wing2.layout_plans( 24, 36 )            # generate building plans

# make the 3d model
ac = ac3d.AC3D( "ukulalela" )
ac.gen_headers( "airframe", 2 )
wing1.build_ac3d( ac )
wing2.build_ac3d( ac )
ac.close()

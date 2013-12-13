#!/usr/bin/env python

try:
    import wing
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import wing

wing = wing.Wing()

# wing layout
wing.units = "in"
wing.load_airfoils("naca633618", "naca4412")
wing.span = 32.0
wing.twist = 0
wing.center = 0.35
wing.set_sweep_angle(0)
wing.set_chord( 7.36, 2.45 )
wing.set_num_stations(20)

# wing structure
wing.leading_edge_diamond = 0.1
wing.add_trailing_edge( width=0.75, height=0.25, shape="flat", part="wing" )

# build the wing parts
wing.build()

# create lasercut sheets
wing.layout_parts_sheets( "vintage-glider", 24, 8 )

# create paper templates
wing.layout_parts_templates( "vintage-glider", 8.5, 11 )

# generate building plans
wing.layout_plans( "vintage-glider", 24, 36 )

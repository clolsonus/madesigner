#!/usr/bin/env python

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

root = airfoil.Airfoil("naca633618", 1000, True)
tip = airfoil.Airfoil("naca0015", 1000, True);

rchord = 8.0
tchord = 4.0
twist = 10

width_in = 8.5
height_in = 11
dpi = 90

# show blending airfoils, scaling, rotating, and positioning
print "blending demo"
layout = layout.Layout( 'demo-blend.svg', width_in, height_in, dpi )

steps = 8
dp = 1.0 / steps
ypos = 0.1
for p in range(0, steps+1):
    print p
    percent = p*dp

    rib = airfoil.blend( root, tip, percent )
    size = rchord * (1.0 - percent) + tchord * percent
    rib.scale( size, size )
    rib.fit( 500, 0.002 )

    tx = size/3.0
    ty = rib.simple_interp(rib.top, tx)
    by = rib.simple_interp(rib.bottom, tx)
    vd = (ty - by)
    hy = by + vd / 2.0
    rib.add_label( tx, hy, 14, 0, "W" + str(p) )

    rib.rotate( percent * twist )

    bounds = rib.get_bounds()

    layout.draw_airfoil_demo( rib, width_in*0.5, ypos )
        
    dy = bounds[1][1] - bounds[0][1]
    ypos += dy + 0.1

layout.save()

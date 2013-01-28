#!/usr/bin/env python

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

root = airfoil.Airfoil("naca633618", 1000, True)
tip = airfoil.Airfoil("naca0015", 1000, True);

rchord = 8.0
tchord = 4.0
twist = 10

width = 8.5
height = 11

# show blending airfoils, scaling, rotating, and positioning
print "blending demo"
layout = layout.Layout( 'demo-blend', width, height )

steps = 8
dp = 1.0 / steps

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

    pos = contour.Cutpos(percent=0.6)
    rib.trim( side="top", discard="rear", cutpos=pos)

    rib.rotate( percent * twist )

    layout.draw_part_demo( rib )
        
layout.save()

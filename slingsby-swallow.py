#!/usr/bin/env python

import airfoil

from svginstr import *
import sys

root = airfoil.Airfoil("naca633618-smooth", 1000, True)
tip = airfoil.Airfoil("naca4412", 1000, True);
#root.display()
#tip.display()

dim1 = 1520
blend1 = airfoil.blend( root, tip, 1.0 )
blend1.fit( 500, 0.0001 )
#blend1.display()
print len(blend1.top)
print len(blend1.bottom)
blend1.scale(dim1, dim1)
blend1.move(-dim1 / 3.0, 0)
blend1.rotate(0)
blend1.cutout_stringer( "top", "vertical", 0, 25, 35 )
blend1.cutout_stringer( "bottom", "vertical", 200, 20, 25 )
blend1.cutout_stringer( "top", "tangent", -400, 25, 25 )
blend1.cutout_stringer( "top", "tangent", 800, 25, 25 )
blend1.cutout_stringer( "bottom", "tangent", -450, 25, 25 )
blend1.cutout_stringer( "bottom", "vertical", 700, 25, 25 )
blend1.cutout_sweep( "top", -500, 100, 10, 10 )
blend1.cutout_sweep( "top", -350, 300, 10, 10 )
blend1.cutout_sweep( "bottom", -175, 350, 10, 10 )
blend1.scale(0.1, 0.1)
#blend1.display()

dim2 = 1010
blend2 = airfoil.blend( root, tip, 0.5 )
blend2.scale(dim2, dim2)
blend2.move( -dim2 / 3.0, 0 )
blend2.rotate( 2.5 )
blend2.cutout_stringer( "top", "vertical", 0, 25, 35 )
blend2.cutout_stringer( "bottom", "vertical", 200, 20, 25 )
#blend2.display()

dim3 = 500
blend3 = airfoil.blend( root, tip, 0.0 )
blend3.scale(dim3, dim3)
blend3.move( -dim3 / 3.0, 0 )
blend3.rotate( 5 )
blend3.cutout_stringer( "top", "vertical", 0, 25, 35 )
blend3.cutout_stringer( "bottom", "vertical", 200, 20, 25 )
#blend3.display()

a = Instrument("slingsby-swallow.svg", 2000, 1000, "slingsby swallow", "cm")

first = True
reverse_top = list(blend1.top)
reverse_top.reverse()
p = Path().abs()
for pt in reverse_top:
    if first:
        p.moveto( pt[0], pt[1] )
        first = False
    else:
        p.lineto( pt[0], pt[1] )
for pt in blend1.bottom:
    p.lineto( pt[0], pt[1] )
p.close()

a.begin()
a.shape(p, stroke = "red", stroke_width = 0.1, fill = "none")
a.end()

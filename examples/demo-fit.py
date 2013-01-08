#!/usr/bin/env python

import copy
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
twist = -10

width_in = 8.5
height_in = 11
margin_in = 0.1
dpi = 90

print "resampling and adaptive fit demo"
layout = layout.Layout( 'demo-fit', width_in, height_in, margin_in, dpi )

root = airfoil.Airfoil("naca633618", 0, False)

rib = copy.deepcopy(root)
rib.scale( rchord, rchord )
tx = rchord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Original Points" )
layout.draw_airfoil_vertices( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( rchord, rchord )
rib.fit( 200, 0.00005 )
tx = rchord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.00005\" tolerance" )
layout.draw_airfoil_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( rchord, rchord )
rib.fit( 200, 0.0005 )
tx = rchord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.0005\" tolerance" )
layout.draw_airfoil_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( rchord, rchord )
rib.fit( 200, 0.005 )
tx = rchord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.005\" tolerance" )
layout.draw_airfoil_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( rchord, rchord )
rib.fit( 200, 0.01 )
tx = rchord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.01\" tolerance" )
layout.draw_airfoil_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( rchord, rchord )
rib.fit( 200, 0.05 )
tx = rchord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.05\" tolerance" )
layout.draw_airfoil_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( rchord, rchord )
rib.fit( 200, 0.1 )
tx = rchord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.1\" tolerance" )
layout.draw_airfoil_demo( rib )

layout.save_all()

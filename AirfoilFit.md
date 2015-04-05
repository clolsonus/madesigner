# Airfoil Spline Interpolation, Resampling, and Fitting #

The basic airfoil manipulation library provides functions to fit a spline
curve through the airfoil polygon.  The airfoil can be resampled at a higher
sample rate from the spline curve.  Finally the higher resolution sample
can be fit with a lower resolution polygon that matches the original curve
within some specified error tolerance.


# Details #

The following image shows the original airfoil polygon data plot.  It then
shows curved spline interpolation of the original points, resampling at a
much finer step size, and then adaptive fitting to incrementally coarser
error tolerances.

The spline curve is fit parametricly which allows it to be wrapped smoothly
around the nose.

![http://wiki.madesigner.googlecode.com/git/images/demo-fit0.png](http://wiki.madesigner.googlecode.com/git/images/demo-fit0.png)

# Code #

```
#!/usr/bin/env python

import copy
import svgwrite
import airfoil
import layout

chord = 8.0

width = 8.5
height = 11

print "resampling and adaptive fit demo"
layout = layout.Layout( 'demo-fit', width, height )

root = airfoil.Airfoil("naca633618", 0, False)

rib = copy.deepcopy(root)
rib.scale( chord, chord )
tx = chord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Original Points" )
layout.draw_part_vertices( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( chord, chord )
rib.fit( 200, 0.00005 )
tx = chord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.00005\" tolerance" )
layout.draw_part_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( chord, chord )
rib.fit( 200, 0.0005 )
tx = chord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.0005\" tolerance" )
layout.draw_part_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( chord, chord )
rib.fit( 200, 0.005 )
tx = chord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.005\" tolerance" )
layout.draw_part_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( chord, chord )
rib.fit( 200, 0.01 )
tx = chord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.01\" tolerance" )
layout.draw_part_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( chord, chord )
rib.fit( 200, 0.05 )
tx = chord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.05\" tolerance" )
layout.draw_part_demo( rib )

rib = copy.deepcopy(root)
rib.resample(1000, True)
rib.scale( chord, chord )
rib.fit( 200, 0.1 )
tx = chord/3.0
ty = rib.simple_interp(rib.top, tx)
by = rib.simple_interp(rib.bottom, tx)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( tx, hy, 14, 0, "Spline interpolation & adaptive fit to 0.1\" tolerance" )
layout.draw_part_demo( rib )

layout.save()
```
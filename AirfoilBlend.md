# Airfoil Shape Interpolation #

The basic airfoil manipulation library allows incrementally blending between two different airfoils


# Details #

In the following figure notice the difference between the starting and ending airfoil shapes.  Rib W0 is NACA63(3)618 and Rib W8 is NACA0015.  Also notice the adaptive point fit evolve from start to finish.  Also shown is the ability to scale and rotate airfoils to any size or orientation.

![http://wiki.madesigner.googlecode.com/git/images/demo-blend0.png](http://wiki.madesigner.googlecode.com/git/images/demo-blend0.png)

# Code #

```
import svgwrite
import airfoil
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

    rib.rotate( percent * twist )

    layout.draw_part_demo( rib )
        
layout.save()
```
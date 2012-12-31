#!/usr/bin/env python

import svgwrite

try:
    import airfoil
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import airfoil

rib = airfoil.Airfoil("naca0015", 1000, True)
#rib = airfoil.Airfoil("naca0015", )

chord = 8.0
span = 30.0

width_in = 8.5
height_in = 11
stroke_width_in = 0.01
dpi = 90

def draw_airfoil_svg( dwg, airfoil, xpos, ypos, lines = True, points = False ):
    bounds = airfoil.get_bounds()
    dx = bounds[1][0] - bounds[0][0]
    dy = bounds[1][1] - bounds[0][1]

    marginx = (width_in - dx) * 0.5
    marginy = (height_in - dy) * 0.5
    
    airfoil.scale( dpi, dpi )
    reverse_top = list(airfoil.top)
    reverse_top.reverse()
    shape = reverse_top + airfoil.bottom
    g = dwg.g()
    g.translate((marginx-bounds[0][0])*dpi,(ypos-bounds[0][1])*dpi)
    if lines:
        poly = dwg.polygon(shape, stroke = 'red', fill = 'none', \
                               stroke_width = '{:.4f}in'.format(stroke_width_in))
        g.add( poly )

    if points:
        for pt in shape:
            c = dwg.circle( center = pt, r = 2, stroke = 'green', \
                                fill = 'green', opacity = 0.6)
            g.add(c)

    t = dwg.text(airfoil.description, (0.25*dpi, 0.0*dpi))
    g.add(t)

    dwg.add(g)

dwg = svgwrite.Drawing( 'super-sportster-wing.svg', size = ( '{:.2f}in'.format(width_in), '{:.2f}in'.format(height_in) ) )

rib.fit( 500, 0.0001 )
rib.scale( chord, chord )
rib.move(-chord / 3.0, 0)

bounds = rib.get_bounds()


# leading edge sheeting (before washout rotate)
le = bounds[0][0] + 0.120
d = chord * 0.3
rib.cutout_sweep( "top", bounds[0][0], 12, 0.0625 )
rib.cutout_sweep( "bottom", bounds[0][0], 12, 0.0625 )
#rib.cutout_sweep( "top", le, d, 0.0625, 0.05 )
#rib.cutout_sweep( "bottom", le, d, 0.0625, 0.05 )

rib.cutout_leading_edge_diamond( 0.250 - 0.0625 )

# rear stringer (before washout rotate)
rs = bounds[1][0] - chord*0.5
fs = -chord * 0.2
rib.cutout_stringer( "top", "tangent", rs, 0.125, 0.125 )
rib.cutout_stringer( "bottom", "tangent", rs, 0.125, 0.125 )
rib.cutout_stringer( "top", "tangent", fs, 0.125, 0.125 )
rib.cutout_stringer( "bottom", "tangent", fs, 0.125, 0.125 )

#rib.rotate( (1 - percent) * twist )

# main spars
rib.cutout_stringer( "top", "vertical", 0, 0.250, 0.250 )
rib.cutout_stringer( "bottom", "vertical", 0, 0.250, 0.250 )
         
draw_airfoil_svg( dwg, rib, width_in*0.5, 0, True, True )

dwg.save()

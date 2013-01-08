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

    for hole in airfoil.holes:
        pt = ( hole[0], hole[1] )
        radius = hole[2]
        c = dwg.circle( center = pt, r = radius, stroke = 'red', \
                            fill = 'none', \
                            stroke_width = '{:.4f}in'.format(stroke_width_in))
        g.add(c)

    for label in airfoil.labels:
        t = dwg.text(label[4], (label[0], label[1]), font_size = label[2], text_anchor = "middle")
        t.rotate(label[3] + 180)
        # text_align = center
        g.add(t)

    if points:
        for pt in shape:
            c = dwg.circle( center = pt, r = 2, stroke = 'green', \
                                fill = 'green', opacity = 0.6)
            g.add(c)

    dwg.add(g)

dwg = svgwrite.Drawing( 'sport-flyer-wing.svg', size = ( '{:.2f}in'.format(width_in), '{:.2f}in'.format(height_in) ) )

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


#rib.rotate( (1 - percent) * twist )

# main spars
rib.cutout_stringer( "top", "vertical", 0, 0.250, 0.250 )
rib.cutout_stringer( "bottom", "vertical", 0, 0.250, 0.250 )

# label at 0 pt
ty = rib.simple_interp(rib.top, 0.0)
by = rib.simple_interp(rib.bottom, 0.0)
vd = (ty - by)
hy = by + vd / 2.0
rib.add_label( 0.0, hy, 14, 0, "W1" )

rib.rotate(-10)

# build alignment tabs
at = bounds[1][0] - chord * 0.2
rib.add_build_tab("bottom", at, 0.5, 0.25 )
rib.add_build_tab("bottom", fs-0.5, 0.5 )
rib.add_build_tab("top", fs-0.5, 0.3, 0.25 )

draw_airfoil_svg( dwg, rib, width_in*0.5, 0, True, True )

dwg.save()
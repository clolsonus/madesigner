#!/usr/bin/env python

import airfoil
import svgwrite

do_blending = False
do_resampling = False
do_cutting = True

root = airfoil.Airfoil("naca633618", 1000, True)
tip = airfoil.Airfoil("naca4412", 1000, True);

rchord = 8.0
tchord = 2.632
twist = -10

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

# show blending airfoils, scaling, rotating, and positioning
if do_blending:
    print "blending demo"
    dwg = svgwrite.Drawing( 'demo-blend.svg', size = ( '{:.2f}in'.format(width_in), '{:.2f}in'.format(height_in) ) )
    steps = 9
    dp = 1.0 / steps
    ypos = 0.1
    for p in range(0, steps+1):
        percent = 1 - p*dp

        blend = airfoil.blend( root, tip, percent )
        blend.fit( 500, 0.0001 )
        size = rchord * percent + tchord * (1.0 - percent)
        blend.scale( size, -size )
        blend.rotate( (1 - percent) * twist )

        bounds = blend.get_bounds()

        draw_airfoil_svg( dwg, blend, width_in*0.5, ypos, True, False )

        dy = bounds[1][1] - bounds[0][1]
        ypos += dy + 0.1
    dwg.save()

# show resampling, smoothing, and fitting
if do_resampling:
    print "resampling and adaptive fit demo"
    dwg = svgwrite.Drawing( 'demo-fit.svg', size = ( '{:.2f}in'.format(width_in), '{:.2f}in'.format(height_in) ) )
    ypos = 0.1

    root = airfoil.Airfoil("naca633618", 0, False)
    base_desc = root.description
    root.scale( rchord, -rchord )
    bounds = root.get_bounds()
    dy = bounds[1][1] - bounds[0][1]
    root.description = base_desc + " Original Points"
    draw_airfoil_svg( dwg, root, width_in*0.5, ypos, False, True )

    root.resample(1000, True)
    root.scale( rchord, -rchord )
    root.fit( 200, 0.00005 )
    bounds = root.get_bounds()
    dy = bounds[1][1] - bounds[0][1]
    root.description = base_desc + " Original Points"
    draw_airfoil_svg( dwg, root, width_in*0.5, ypos, True, False )
    ypos += dy + 0.1

    root.resample(1000, True)
    root.scale( rchord, -rchord )
    root.fit( 200, 0.00005 )
    bounds = root.get_bounds()
    dy = bounds[1][1] - bounds[0][1]
    root.description = base_desc + " Adaptive fit to 0.00005\" tolerance"
    draw_airfoil_svg( dwg, root, width_in*0.5, ypos, True, True )
    ypos += dy + 0.1

    root.resample(1000, True)
    root.scale( rchord, -rchord )
    root.fit( 200, 0.0005 )
    bounds = root.get_bounds()
    dy = bounds[1][1] - bounds[0][1]
    root.description = base_desc + " Adaptive fit to 0.0005\" tolerance"
    draw_airfoil_svg( dwg, root, width_in*0.5, ypos, True, True )
    ypos += dy + 0.1

    root.resample(1000, True)
    root.scale( rchord, -rchord )
    root.fit( 200, 0.005 )
    bounds = root.get_bounds()
    dy = bounds[1][1] - bounds[0][1]
    root.description = base_desc + " Adaptive fit to 0.005\" tolerance"
    draw_airfoil_svg( dwg, root, width_in*0.5, ypos, True, True )
    ypos += dy + 0.1

    root.resample(1000, True)
    root.scale( rchord, -rchord )
    root.fit( 200, 0.05 )
    bounds = root.get_bounds()
    dy = bounds[1][1] - bounds[0][1]
    root.description = base_desc + " Adaptive fit to 0.05\" tolerance"
    draw_airfoil_svg( dwg, root, width_in*0.5, ypos, True, True )
    ypos += dy + 0.1

    dwg.save()

if do_cutting:
    print "cutout demos"
    dwg = svgwrite.Drawing( 'demo-cutouts.svg', size = ( '{:.2f}in'.format(width_in), '{:.2f}in'.format(height_in) ) )
    steps = 9
    dp = 1.0 / steps
    ypos = 0.1
    for p in range(0, steps+1):
        print p
        percent = 1 - p*dp

        blend = airfoil.blend( root, tip, percent )
        blend.fit( 500, 0.0001 )
        size = rchord * percent + tchord * (1.0 - percent)
        blend.scale( size, -size )
        blend.move(-size / 3.0, 0)

        bounds = blend.get_bounds()

        # leading edge diamond (before washout rotate)
        print "cutout leading edge"
        blend.cutout_leading_edge_diamond( 0.200 )

        # leading edge sheeting (before washout rotate)
        le = bounds[0][0] + 0.125
        d = size * 0.2
        #blend.cutout_sweep( "top", le, d, 0.0625, 0.05 )
        #blend.cutout_sweep( "bottom", le, d, 0.0625, 0.05 )

        # rear stringer (before washout rotate)
        print "rear stringer"
        rs = bounds[1][0] - tchord*0.5
        blend.cutout_stringer( "top", "vertical", rs, 0.125, 0.125 )
        blend.cutout_stringer( "bottom", "vertical", rs, 0.125, 0.125 )

        #blend.rotate( (1 - percent) * twist )

        # main spars
        print "main spars"
        blend.cutout_stringer( "top", "vertical", 0, 0.125, 0.125 )
        blend.cutout_stringer( "bottom", "vertical", 0, 0.125, 0.125 )
        
 
        draw_airfoil_svg( dwg, blend, width_in*0.5, ypos, True, False )

        dy = bounds[1][1] - bounds[0][1]
        ypos += dy + 0.1
    dwg.save()

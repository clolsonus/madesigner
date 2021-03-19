#!/usr/bin/env python3

# this is a quick test to compute dimensions for a flight test style
# folded foam board wing ... losely based on the clarky airfoil sorta
# kinda

import argparse
import math
import matplotlib.pyplot as plt
import numpy as np

from ft_profile import FtProfile, my_dist

ap = argparse.ArgumentParser(description="Compute the dimensions of FT-style folded wing.  All dimensions are mm unless otherwise noted.")
ap.add_argument('root_chord_mm', type=float, nargs='?', help='root chord')
ap.add_argument('tip_chord_mm', type=float, nargs='?', help='tip chord')
ap.add_argument('span_mm', type=float, nargs='?', help='1/2 span')
ap.add_argument('sweep_mm', type=float, nargs='?', help='sweep offset from straight at tip')
ap.add_argument('inner_dihedral_deg', type=float, nargs='?', help='inner dihedral angle')
ap.add_argument('outer_dihedral_deg', type=float, nargs='?', help='outer dihedral angle')
ap.add_argument('--material_mm', type=float, default=4.9,
                help='material thickness')
#ap.add_argument('--span_mm', type=float, help=
args = ap.parse_args()
#print(args)

def parse_val(val):
    if not len(val):
        print("No response, assuming 0.0")
        return 0
    else:
        try:
            return float(val)
        except:
            print("Entry is not a valid number, aborting, sorry...")
            quit()
    
# do prompts if values aren't passed on the command line
if not args.root_chord_mm:
    val = input("Enter root chord (mm): ")
    args.root_chord_mm = parse_val(val)
if not args.root_chord_mm:
    print("Cannot continue without a root chord size, sorry...")
    quit()
if not args.tip_chord_mm:
    val = input("Enter tip chord (mm): ")
    args.tip_chord_mm = parse_val(val)
if args.tip_chord_mm:
    if not args.span_mm:
        val = input("Enter wing 1/2 span (mm): ")
        args.span_mm = parse_val(val)
    if args.sweep_mm is None:
        val = input("Enter leading edge sweep at tip (mm): ")
        args.sweep_mm = parse_val(val)
    if args.inner_dihedral_deg is None:
        val = input("Enter dihedral angle at root (deg): ")
        args.inner_dihedral_deg = parse_val(val)
    if args.outer_dihedral_deg is None:
        val = input("Enter dihedral angle at tip (deg): ")
        args.outer_dihedral_deg = parse_val(val)

# units: let's do mm
r2d = 180 / math.pi
d2r = math.pi / 180

root = FtProfile(args.root_chord_mm, args.material_mm)
root.compute()
root.plot()

if not args.tip_chord_mm:
    print("simple root profile finished, thank you!")
    quit()

# proceeding with a full wing
if not args.span_mm:
    print("Cannot generate a whole wing plan without a valid span, sorry...")
    quit()
    
tip = FtProfile(args.tip_chord_mm, args.material_mm)
tip.compute()
tip.plot()

if args.sweep_mm:
    tip.outer += np.array([args.sweep_mm, 0])
    tip.spar += np.array([args.sweep_mm, 0])
    
# https://stackoverflow.com/questions/55816902/finding-the-intersection-of-two-circles
def get_intersections(p0, r0, p1, r1):
    # circle 1: (p0[0], p0[1]), radius r0
    # circle 2: (p1[0], p1[1]), radius r1

    print(p0, r0, p1, r1)
    d=math.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)
    
    # non intersecting
    if d > r0 + r1 :
        print("non interesecting circles")
        return None
    # One circle within other
    if d < abs(r0-r1):
        print("one circle inside the other")
        return None
    # coincident circles
    if d == 0 and r0 == r1:
        print("coincident circles")
        return None
    else:
        a=(r0**2-r1**2+d**2)/(2*d)
        h=math.sqrt(r0**2-a**2)
        x2=p0[0]+a*(p1[0]-p0[0])/d   
        y2=p0[1]+a*(p1[1]-p0[1])/d   
        x3=x2+h*(p1[1]-p0[1])/d     
        y3=y2-h*(p1[0]-p0[0])/d 

        x4=x2-h*(p1[1]-p0[1])/d
        y4=y2+h*(p1[0]-p0[0])/d
        
        return (x3, y3, x4, y4)

margin = 5                      # mm
dih_in = args.inner_dihedral_deg
dih_out = args.outer_dihedral_deg

def do_dihedral(orig, angle, side):
    pt = orig.copy()
    a = 0.5 * angle * d2r
    d = pt[1]
    pt[1] = math.cos(a)*d
    if side == "inner":
        pt[2] = math.sin(a)*d
    else:
        pt[2] -= math.sin(a)*d
    return pt

# unfold the vertical 2d coordinates (with implied 3rd dimension due
# to span) into a new 2d top down space.  This is intended to create
# cut files that will fold back together into the correct desired
# shape without weird nonsense over/under lap due to taper.
def unfold(root, tip):
    cuts = []
    scores = []
    
    r_last = do_dihedral(np.hstack([root[0], 0]), dih_in, "inner")
    t_last = do_dihedral(np.hstack([tip[0], args.span_mm]), dih_out, "outer")
    dist = my_dist(r_last, t_last)
    p1_last = [margin, margin]
    p2_last = [margin+dist, margin]
    cuts.append( [p1_last, p2_last] )
    print(r_last, t_last, p1_last, p2_last)
    sections = len(root)-1
    for i in range(sections):
        r = do_dihedral(np.hstack([root[i+1], 0]), dih_in, "inner")
        t = do_dihedral(np.hstack([tip[i+1], args.span_mm]), dih_out, "outer")
        print(r, t)

        a = my_dist(r_last, t_last)
        b = my_dist(r_last, r)
        c = my_dist(t_last, r)
        d = my_dist(t_last, t)
        e = my_dist(r_last, t)
        print(a, b, c, d, e)

        x3, y3, x4, y4 = get_intersections(p1_last, b, p2_last, c)
        if y3 > y4:
            p1 = [ x3, y3 ]
        else:
            p1 = [ x4, y4 ]
        x3, y3, x4, y4 = get_intersections(p1_last, e, p2_last, d)
        if y3 > y4:
            p2 = [ x3, y3 ]
        else:
            p2 = [ x4, y4 ]

        if i == sections - 1:
            cuts.append( [p1, p2] )
        else:
            scores.append( [p1, p2] )
        cuts.append( [p1_last, p1] )
        cuts.append( [p2_last, p2] )

        r_last = r
        t_last = t
        p1_last = p1
        p2_last = p2
    return cuts, scores

def do_plot(cuts, scores):
    # draw a plot of the unfolded layout
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.grid()
    ax.set_aspect("equal")
    for seg in cuts:
        x, y = np.array([seg[0], seg[1]]).T
        ax.plot( x, y, color="r")
    for seg in scores:
        x, y = np.array([seg[0], seg[1]]).T
        ax.plot( x, y, color="b")
    plt.show()

from svgwrite import Drawing, mm
def do_svg(file, cuts, scores):
    # attempt to generate an svg "true scale" drawing
    width = 762                     # 762mm = 30"
    height = 508                    # 508mm = 20"
    units = "mm"
    dpi = 96 / 25.4                 # for mm
    dwg = Drawing( file, size = ("%d%s" % (width, units),
                                 "%d%s" % (height, units)) )
    dwg.viewbox(0, 0, width*dpi, height*dpi)
    g = dwg.g()                 # group
    dwg.add(g)
    for seg in cuts:
        line = dwg.line([seg[0][0]*mm, seg[0][1]*mm],
                        [seg[1][0]*mm, seg[1][1]*mm],
                        stroke='red', fill='none', stroke_width="1px")
        g.add( line )
    for seg in scores:
        line = dwg.line([seg[0][0]*mm, seg[0][1]*mm],
                        [seg[1][0]*mm, seg[1][1]*mm],
                        stroke='blue', fill='none', stroke_width="1px")
        g.add( line )
    dwg.save()
    
cuts, scores = unfold(root.outer, tip.outer)
do_plot(cuts, scores)
do_svg("unfolded-wing.svg", cuts, scores)

cuts, scores = unfold(root.spar, tip.spar)
do_plot(cuts, scores)
do_svg("unfolded-spar.svg", cuts, scores)


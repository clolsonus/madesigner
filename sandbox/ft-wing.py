#!/usr/bin/env python3

# this is a quick test to compute dimensions for a flight test style
# folded foam board wing ... losely based on the clarky airfoil sorta
# kinda

import argparse
import math
import matplotlib.pyplot as plt
import numpy as np

ap = argparse.ArgumentParser(description="Compute the dimensions of FT-style folded wing.  All dimensions are mm unless otherwise noted.")
ap.add_argument('chord_mm', type=int, help='desired chord')
ap.add_argument('--material_mm', type=float, default=4.9, help='material thickness')
args = ap.parse_args()

# units: let's do mm
r2d = 180 / math.pi

material_mm = args.material_mm  # defaults to 5 hopefully

# clarky numbers
max_thickness_perc = 0.117      # vertically proportional to chord
max_point_perc = .309           # longitudinally proportional to chord
le_raise_perc = .28             # vertically proportional to max height

# basic proportions
spar_perc = 0.20                # longitudinally proportional to chord
aileron_perc = 0.23             # desired overhang for ailerons

# edit this to size wing
chord_mm = args.chord_mm
print("wing chord mm: %.0f" % chord_mm)

# compute things
max_mm = chord_mm * max_thickness_perc
print("max thickness mm: %.0f" % max_mm)

le_height_mm = max_mm * le_raise_perc

spar_width_mm = chord_mm * spar_perc
spar_height_mm = max_mm - 2*material_mm
print("spar width mm: %.0f" % spar_width_mm)
print("spar height mm: %.0f" % spar_height_mm)
print("spar cuts: %.0f %.0f %.0f %.0f %.0f" % (spar_height_mm, spar_height_mm+material_mm, spar_height_mm+spar_width_mm-material_mm, spar_height_mm+spar_width_mm, 2*spar_height_mm + spar_width_mm))

max_point_mm = chord_mm * max_point_perc
half_spar = spar_width_mm * 0.5
spar_start_mm = max_point_mm - half_spar
spar_end_mm = max_point_mm + half_spar
print("spar start mm: %.0f" % spar_start_mm)
print("spar end mm: %.0f" % spar_end_mm)

le_crease_mm = spar_start_mm * 0.5
print("leading edge crease mm: %.0f" % le_crease_mm)

ail_overhang_mm = chord_mm * aileron_perc
print("desired aileron overhang mm: %.0f" % ail_overhang_mm)

# do trigs
aft_dist = chord_mm - spar_end_mm
print(aft_dist)
h = max_mm - material_mm
aft_hyp = math.sqrt( (h*h) + (aft_dist*aft_dist) )
print(aft_hyp)
angle = math.asin(h/aft_hyp)
print("angle deg:", angle*r2d)

mat2 = material_mm*1.9          # technical 2*mat, but allow for compression
act_overhang_mm = mat2 / math.tan(angle)
print("actual overhang: %.0f" % act_overhang_mm)

# inner points
nose = [material_mm, le_height_mm]
bot_front_spar = [spar_start_mm, material_mm]
bot_rear_spar = [spar_end_mm, material_mm]
top_front_spar = [spar_start_mm, max_mm-material_mm]
top_rear_spar = [spar_end_mm, max_mm-material_mm]
bot_te = [chord_mm-act_overhang_mm, material_mm]
final_te = [chord_mm, 0]
inner = np.array([bot_te,
                  bot_rear_spar,
                  bot_front_spar,
                  nose,
                  top_front_spar,
                  top_rear_spar,
                  final_te
                  ])

# outer points
nose_bot = [0, le_height_mm - material_mm*0.5]
nose_true = [0, le_height_mm]
nose_top = [0, le_height_mm + material_mm*0.5]
bot_front_spar = [spar_start_mm, 0]
bot_rear_spar = [spar_end_mm, 0]
top_front_spar = [spar_start_mm, max_mm]
top_rear_spar = [spar_end_mm, max_mm]
bot_te = [chord_mm-act_overhang_mm, 0]
final_te = [chord_mm, material_mm]
# dance
xdiff = spar_start_mm
ydiff = max_mm - nose_top[1]
len = math.sqrt(xdiff*xdiff + ydiff*ydiff)
base = [nose_top[0] + xdiff*0.5, nose_top[1] + ydiff*0.5]
xoff = -ydiff*0.05
yoff = xdiff*0.05
crease = [base[0]+xoff, base[1]+yoff]
outer = np.array([bot_te,
                  # bot_rear_spar,
                  bot_front_spar,
                  nose_bot,
                  nose_true,
                  nose_top,
                  crease,
                  top_front_spar,
                  top_rear_spar,
                  final_te
                  ])

# spar points
spar_tf = [spar_start_mm, max_mm-material_mm]
spar_bf = [spar_start_mm, material_mm]
spar_br = [spar_end_mm, material_mm]
spar_tr = [spar_end_mm, max_mm-material_mm]
spar_itf = [spar_start_mm+material_mm, max_mm-material_mm]
spar_ibf = [spar_start_mm+material_mm, 2*material_mm]
spar_ibr = [spar_end_mm-material_mm, 2*material_mm]
spar_itr = [spar_end_mm-material_mm, max_mm-material_mm]
spar = np.array([spar_tf, spar_bf, spar_br, spar_tr,
                 spar_itr, spar_ibr, spar_ibf, spar_itf, spar_tf])

# trailing spacer
lte = chord_mm-act_overhang_mm
ts_br = [lte, material_mm]
ts_bf = [lte-2.5*material_mm, material_mm]
ts_tf = [lte-2.5*material_mm, 2*material_mm]
ts_tr = [lte, 2*material_mm]
trailing = np.array([ts_br, ts_bf, ts_tf, ts_tr, ts_br])

le_pad = (material_mm*2*math.pi)/4 - material_mm
print("leading edge radius pad: %.1f" % le_pad)

def my_dist(p1, p2, pad=0):
    return np.linalg.norm( np.array(p1) - np.array(p2) ) + pad

def my_annotate(ax, text, p1, p2):
    p = (np.array(p1) + np.array(p2))*0.5
    pt = p.copy()
    #if side == "top":
    #    pt[1] += material_mm
    #else:
    #    pt[1] -= material_mm
    ax.annotate(text, xy=p, xytext=pt)
    #arrowprops=dict(facecolor='black', shrink=0.05),
    #horizontalalignment='right', verticalalignment='top')

A = my_dist(outer[0], outer[1])
B = my_dist(outer[1], outer[2], le_pad)
C = my_dist(outer[4], outer[5], le_pad)
D = my_dist(outer[5], outer[6])
E = my_dist(outer[6], outer[7])
F = my_dist(outer[7], outer[8])
segments = [A, B, C, D, E, F]

print("Wing segments unfolded:")
accum = A
print("A: %.0f Cumulative: %.0f mm" % (A, accum))
accum += B
print("B: %.0f Cumulative: %.0f mm" % (B, accum))
accum += C
print("C: %.0f Cumulative: %.0f mm" % (C, accum))
accum += D
print("D: %.0f Cumulative: %.0f mm" % (D, accum))
accum += E
print("E: %.0f Cumulative: %.0f mm" % (E, accum))
accum += F
print("F: %.0f Cumulative: %.0f mm" % (F, accum))
print("Total (mm): %.0f" % np.sum(segments) )

print("Spar:")
w = my_dist(spar_bf, spar_br)
h =  my_dist(spar_tf, spar_bf)
print("width: %.0f mm" % w)
print("height: %.0f mm" % h)
print("Total(mm): %.0f" % (w + 2*h))

print("Trailing edge spacer:")
print("width: %.0f mm" % (2.5*material_mm))
      
# plot
fig = plt.figure()
ax = fig.add_subplot()
#outer
x, y = outer.T
ax.scatter( x, y, marker=".", color="g" )
ax.plot( x, y, color="r" )
#x, y = inner.T
#ax.scatter( x, y, marker=".", color="g" )
#ax.plot( x, y, color="b")
# spar
x, y = spar.T
ax.scatter( x, y, marker=".", color="g" )
ax.plot( x, y, color="b" )
# trailing spacer
x, y = trailing.T
ax.scatter( x, y, marker=".", color="g" )
ax.plot( x, y, color="b" )

my_annotate(ax, "A %.0f" % A, outer[0], outer[1])
my_annotate(ax, "B %.0f" % B, outer[1], outer[2])
my_annotate(ax, "C %.0f" % C, outer[4], outer[5])
my_annotate(ax, "D %.0f" % D, outer[5], outer[6])
my_annotate(ax, "E %.0f" % E, outer[6], outer[7])
my_annotate(ax, "F %.0f" % F, outer[7], outer[8])
ax.set_aspect('equal')
ax.grid()
ax.set_title("Chord: %.0f (mm)  Perimeter total: %.0f (mm)" % (chord_mm, np.sum(segments)))
ax.set_xlabel("Units = mm")
plt.show()

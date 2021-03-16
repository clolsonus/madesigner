#!/usr/bin/env python3

# this is a quick test to compute dimensions for a flight test style
# folded foam board wing ... losely based on the clarky airfoil sorta
# kinda

import math
import matplotlib.pyplot as plt
import numpy as np

# units: let's do mm
r2d = 180 / math.pi

def my_dist(p1, p2, pad=0):
    return np.linalg.norm( np.array(p1) - np.array(p2) ) + pad

def my_annotate(ax, label, p1, p2):
    p = (np.array(p1) + np.array(p2))*0.5
    pt = p.copy()
    #if side == "top":
    #    pt[1] += self.material_mm
    #else:
    #    pt[1] -= self.material_mm
    ax.annotate(label, xy=p, xytext=pt)
    #arrowprops=dict(facecolor='black', shrink=0.05),
    #horizontalalignment='right', verticalalignment='top')

class FtProfile():
    # clarky numbers
    max_thickness_perc = 0.117      # vertically proportional to chord
    max_point_perc = .309           # longitudinally proportional to chord
    le_raise_perc = .28             # vertically proportional to max height

    # basic proportions
    spar_perc = 0.20                # longitudinally proportional to chord
    aileron_perc = 0.23             # desired overhang for ailerons

    def __init__(self, chord_mm, material_mm=4.9):
        self.chord_mm = chord_mm
        self.material_mm = material_mm
        self.inner = []
        self.outer = []
        self.seglens = []
        self.spar = []
        self.trailing = []
        
    def compute(self):
        print("wing chord mm: %.0f" % self.chord_mm)

        max_mm = self.chord_mm * self.max_thickness_perc
        print("max thickness mm: %.0f" % max_mm)

        le_height_mm = max_mm * self.le_raise_perc

        spar_width_mm = self.chord_mm * self.spar_perc
        spar_height_mm = max_mm - 2*self.material_mm
        print("spar width mm: %.0f" % spar_width_mm)
        print("spar height mm: %.0f" % spar_height_mm)
        print("spar cuts: %.0f %.0f %.0f %.0f %.0f" % (spar_height_mm, spar_height_mm+self.material_mm, spar_height_mm+spar_width_mm-self.material_mm, spar_height_mm+spar_width_mm, 2*spar_height_mm + spar_width_mm))

        self.max_point_mm = self.chord_mm * self.max_point_perc
        half_spar = spar_width_mm * 0.5
        spar_start_mm = self.max_point_mm - half_spar
        spar_end_mm = self.max_point_mm + half_spar
        print("spar start mm: %.0f" % spar_start_mm)
        print("spar end mm: %.0f" % spar_end_mm)

        le_crease_mm = spar_start_mm * 0.5
        print("leading edge crease mm: %.0f" % le_crease_mm)

        ail_overhang_mm = self.chord_mm * self.aileron_perc
        print("desired aileron overhang mm: %.0f" % ail_overhang_mm)

        # do trigs
        aft_dist = self.chord_mm - spar_end_mm
        print(aft_dist)
        h = max_mm - self.material_mm
        aft_hyp = math.sqrt( (h*h) + (aft_dist*aft_dist) )
        print(aft_hyp)
        angle = math.asin(h/aft_hyp)
        print("angle deg:", angle*r2d)

        mat2 = self.material_mm*1.9          # technical 2*mat, but allow for compression
        act_overhang_mm = mat2 / math.tan(angle)
        print("actual overhang: %.0f" % act_overhang_mm)

        # inner points
        nose = [self.material_mm, le_height_mm]
        bot_front_spar = [spar_start_mm, self.material_mm]
        bot_rear_spar = [spar_end_mm, self.material_mm]
        top_front_spar = [spar_start_mm, max_mm-self.material_mm]
        top_rear_spar = [spar_end_mm, max_mm-self.material_mm]
        bot_te = [self.chord_mm-act_overhang_mm, self.material_mm]
        final_te = [self.chord_mm, 0]
        self.inner = np.array([bot_te,
                               bot_rear_spar,
                               bot_front_spar,
                               nose,
                               top_front_spar,
                               top_rear_spar,
                               final_te
                               ])

        # outer points
        nose_bot = [0, le_height_mm - self.material_mm*0.5]
        nose_true = [0, le_height_mm]
        nose_top = [0, le_height_mm + self.material_mm*0.5]
        bot_front_spar = [spar_start_mm, 0]
        bot_rear_spar = [spar_end_mm, 0]
        top_front_spar = [spar_start_mm, max_mm]
        top_rear_spar = [spar_end_mm, max_mm]
        bot_te = [self.chord_mm-act_overhang_mm, 0]
        final_te = [self.chord_mm, self.material_mm]
        # dance
        xdiff = spar_start_mm
        ydiff = max_mm - nose_top[1]
        len = math.sqrt(xdiff*xdiff + ydiff*ydiff)
        base = [nose_top[0] + xdiff*0.5, nose_top[1] + ydiff*0.5]
        xoff = -ydiff*0.05
        yoff = xdiff*0.05
        crease = [base[0]+xoff, base[1]+yoff]
        self.outer = np.array([bot_te,
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
        spar_front_bot = [spar_start_mm, self.material_mm]
        spar_front_top = [spar_start_mm, max_mm-self.material_mm]
        spar_rear_top = [spar_end_mm, max_mm-self.material_mm]
        spar_rear_bot = [spar_end_mm, self.material_mm]
        self.spar = np.array([spar_front_bot, spar_front_top, spar_rear_top,
                              spar_rear_bot])
        
        spar_front1 = [spar_start_mm, self.material_mm]
        spar_front2 = [spar_start_mm, max_mm-self.material_mm]
        spar_front3 = [spar_start_mm+self.material_mm, max_mm-self.material_mm]
        spar_front4 = [spar_start_mm+self.material_mm, self.material_mm]
        spar_mid1 = [spar_start_mm+self.material_mm, max_mm-self.material_mm]
        spar_mid2 = [spar_end_mm-self.material_mm, max_mm-self.material_mm]
        spar_mid3 = [spar_end_mm-self.material_mm, max_mm-2*self.material_mm]
        spar_mid4 = [spar_start_mm+self.material_mm, max_mm-2*self.material_mm]
        spar_rear1 = [spar_end_mm, self.material_mm]
        spar_rear2 = [spar_end_mm, max_mm-self.material_mm]
        spar_rear3 = [spar_end_mm-self.material_mm, max_mm-self.material_mm]
        spar_rear4 = [spar_end_mm-self.material_mm, self.material_mm]
        self.spar_front = np.array([spar_front1, spar_front2, spar_front3,
                                    spar_front4, spar_front1])
        self.spar_mid = np.array([spar_mid1, spar_mid2, spar_mid3, spar_mid4,
                                  spar_mid1])
        self.spar_rear = np.array([spar_rear1, spar_rear2, spar_rear3,
                                   spar_rear4, spar_rear1])
        #spar = np.array([spar_bf, spar_tf, spar_tr, spar_br,
        #                 spar_itr, spar_ibr, spar_ibf, spar_itf, spar_tf])

        # trailing spacer
        lte = self.chord_mm-act_overhang_mm
        ts_br = [lte, self.material_mm]
        ts_bf = [lte-2.5*self.material_mm, self.material_mm]
        ts_tf = [lte-2.5*self.material_mm, 2*self.material_mm]
        ts_tr = [lte, 2*self.material_mm]
        self.trailing = np.array([ts_br, ts_bf, ts_tf, ts_tr, ts_br])

        le_pad = (self.material_mm*2*math.pi)/4 - self.material_mm
        print("leading edge radius pad: %.1f" % le_pad)

        A = my_dist(self.outer[0], self.outer[1])
        B = my_dist(self.outer[1], self.outer[2], le_pad)
        C = my_dist(self.outer[4], self.outer[5], le_pad)
        D = my_dist(self.outer[5], self.outer[6])
        E = my_dist(self.outer[6], self.outer[7])
        F = my_dist(self.outer[7], self.outer[8])
        self.seglens = [A, B, C, D, E, F]

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
        print("Total (mm): %.0f" % np.sum(self.seglens) )

        print("Spar:")
        w = spar_end_mm - spar_start_mm
        h =  max_mm - 2*self.material_mm
        print("width: %.0f mm" % w)
        print("height: %.0f mm" % h)
        print("Total(mm): %.0f" % (w + 2*h))

        print("Trailing edge spacer:")
        print("width: %.0f mm" % (2.5*self.material_mm))

    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot()
        #outer
        x, y = self.outer.T
        ax.scatter( x, y, marker=".", color="g" )
        ax.plot( x, y, color="r" )
        #x, y = self.inner.T
        #ax.scatter( x, y, marker=".", color="g" )
        #ax.plot( x, y, color="b")
        # spar segments
        x, y = self.spar_front.T
        ax.scatter( x, y, marker=".", color="g" )
        ax.plot( x, y, color="b" )
        x, y = self.spar_mid.T
        ax.scatter( x, y, marker=".", color="g" )
        ax.plot( x, y, color="b" )
        x, y = self.spar_rear.T
        ax.scatter( x, y, marker=".", color="g" )
        ax.plot( x, y, color="b" )
        # trailing spacer
        x, y = self.trailing.T
        ax.scatter( x, y, marker=".", color="g" )
        ax.plot( x, y, color="b" )

        my_annotate(ax, "A %.0f" % self.seglens[0],
                    self.outer[0], self.outer[1])
        my_annotate(ax, "B %.0f" % self.seglens[1],
                    self.outer[1], self.outer[2])
        my_annotate(ax, "C %.0f" % self.seglens[2],
                    self.outer[4], self.outer[5])
        my_annotate(ax, "D %.0f" % self.seglens[3],
                    self.outer[5], self.outer[6])
        my_annotate(ax, "E %.0f" % self.seglens[4],
                    self.outer[6], self.outer[7])
        my_annotate(ax, "F %.0f" % self.seglens[5],
                    self.outer[7], self.outer[8])
        ax.set_aspect('equal')
        ax.grid()
        ax.set_title("Chord: %.0f (mm)  Perimeter total: %.0f (mm)" % (self.chord_mm, np.sum(self.seglens)))
        ax.set_xlabel("Units = mm")
        plt.show()

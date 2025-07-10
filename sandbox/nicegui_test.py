import math
import matplotlib.pyplot as plt
from nicegui import ui
import numpy as np
from svgwrite import Drawing, mm
from uuid import uuid4

from ft_profile import FtProfile, my_dist

# units: let's do mm
r2d = 180 / math.pi
d2r = math.pi / 180

root_chord_mm = 100
root_dihedral_deg = 5
tip_dihedral_deg = 0
tip_chord_mm = 100
material_mm = 4.9
halfspan_mm = 400
sweep_mm = 0

class FTWingPlan():
    def __init__(self):
        self.build_page()

    def build_page(self):
        ui.button("Generate Plans", on_click=self.generate_plans)
        with ui.grid(columns=2).classes('items-center'):
            self.enter_root_chord = ui.input(label='Root Chord (mm)', value=200)
            ui.label("")

            self.enter_tip_chord = ui.input(label='Tip Chord (mm)', value="")
            ui.label("(Enter a value > 0 for a tapered wing)")

            self.enter_halfspan = ui.input(label='Wing Half Span (mm)', value=500)
            ui.label("")

            self.enter_sweep = ui.input(label='Sweep (mm)', value="")
            ui.label("(Enter a value > 0 for a swept wing.  Distance start of tip is behind start of root)")

            self.enter_material_thickness = ui.input(label='Material Thickness (mm)', value=4.9)
            ui.label("(Dollar Tree foamboard = 4.9mm)")

            self.enter_root_dihedral = ui.input(label='Root Dihedral (deg)', value=5)
            ui.label("")

            self.enter_tip_dihedral = ui.input(label='Tip Dihedral (deg)', value="")
            ui.label("(Enter a value > 0 for tip dihedral.  Used for Polyhedral wings.)")

        self.root_plot = ui.row()
        self.tip_plot =  ui.row()
        self.wing_plot = ui.row()
        self.spar_plot = ui.row()

    def generate_plans(self):
        # sanity checks on values go here
        if float(self.enter_halfspan.value) < 1:
            print("Cannot generate a whole wing plan without a valid half span, sorry...")
            return

        root_mm = float(self.enter_root_chord.value)
        root = FtProfile(root_mm, float(self.enter_material_thickness.value))
        root.compute()
        self.root_plot.clear()
        with self.root_plot:
            root.plot_ui()

        if len(self.enter_tip_chord.value):
            tip_mm = float(self.enter_tip_chord.value)
        else:
            tip_mm = root_mm
        tip = FtProfile(tip_mm, float(self.enter_material_thickness.value))
        tip.compute()
        self.tip_plot.clear()
        with self.tip_plot:
            tip.plot_ui()

        if len(self.enter_sweep.value):
            sweep_mm = float(self.enter_sweep.value)
        else:
            sweep_mm = 0
        tip.outer += np.array([float(sweep_mm), 0])
        tip.spar += np.array([float(sweep_mm), 0])

        margin = 5  # mm
        root_dih = float(self.enter_root_dihedral.value)
        if len(self.enter_tip_dihedral.value):
            tip_dih = float(self.enter_tip_dihedral.value)
        else:
            tip_dih = 0
        span_mm = float(self.enter_halfspan.value)

        cuts, scores = self.unfold(root.outer, tip.outer, root_dih, tip_dih, span_mm, margin)
        self.wing_plot.clear()
        with self.wing_plot:
            self.do_plot_ui(cuts, scores)
        self.do_svg("unfolded-wing.svg", cuts, scores)

        cuts, scores = self.unfold(root.spar, tip.spar, root_dih, tip_dih, span_mm, margin)
        self.spar_plot.clear()
        with self.spar_plot:
            self.do_plot_ui(cuts, scores)
        self.do_svg("unfolded-spar.svg", cuts, scores)

    def do_dihedral(self, orig, angle, side):
        pt = orig.copy()
        a = 0.5 * angle * d2r
        d = pt[1]
        pt[1] = math.cos(a)*d
        if side == "inner":
            pt[2] = math.sin(a)*d
        else:
            pt[2] -= math.sin(a)*d
        return pt

    # https://stackoverflow.com/questions/55816902/finding-the-intersection-of-two-circles
    def get_intersections(self, p0, r0, p1, r1):
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

    # unfold the vertical 2d coordinates (with implied 3rd dimension due
    # to span) into a new 2d top down space.  This is intended to create
    # cut files that will fold back together into the correct desired
    # shape without weird nonsense over/under lap due to taper.
    def unfold(self, root, tip, root_dih, tip_dih, span_mm, margin):
        cuts = []
        scores = []

        r_last = self.do_dihedral(np.hstack([root[0], 0]), root_dih, "inner")
        t_last = self.do_dihedral(np.hstack([tip[0], span_mm]), tip_dih, "outer")
        dist = my_dist(r_last, t_last)
        p1_last = [margin, margin]
        p2_last = [margin+dist, margin]
        cuts.append( [p1_last, p2_last] )
        print(r_last, t_last, p1_last, p2_last)
        sections = len(root)-1
        for i in range(sections):
            r = self.do_dihedral(np.hstack([root[i+1], 0]), root_dih, "inner")
            t = self.do_dihedral(np.hstack([tip[i+1], span_mm]), tip_dih, "outer")
            print(r, t)

            a = my_dist(r_last, t_last)
            b = my_dist(r_last, r)
            c = my_dist(t_last, r)
            d = my_dist(t_last, t)
            e = my_dist(r_last, t)
            print(a, b, c, d, e)

            x3, y3, x4, y4 = self.get_intersections(p1_last, b, p2_last, c)
            if y3 > y4:
                p1 = [ x3, y3 ]
            else:
                p1 = [ x4, y4 ]
            x3, y3, x4, y4 = self.get_intersections(p1_last, e, p2_last, d)
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

    def do_plot_ui(self, cuts, scores):
        # draw a plot of the unfolded layout
        with ui.matplotlib().figure as fig:
            ax = fig.gca()
            ax.grid()
            ax.set_aspect("equal")
            for seg in cuts:
                x, y = np.array([seg[0], seg[1]]).T
                ax.plot( x, y, color="r")
            for seg in scores:
                x, y = np.array([seg[0], seg[1]]).T
                ax.plot( x, y, color="b")

    def do_svg(self, file, cuts, scores):
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



plan = FTWingPlan()

ui.run()

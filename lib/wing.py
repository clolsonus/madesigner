#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy
import math
import svgwrite

import airfoil
import layout


class Rib:
    def __init__(self):
        self.thickness = 0.0625
        self.material = "balsa"
        self.contour = None
        self.pos = (0.0, 0.0, 0.0)
        self.sweep = 0.0
        self.placed = False


class Wing:

    def __init__(self):
        self.units = "in"

        # wing layout
        self.root = None
        self.tip = None
        self.root_chord = 10.0
        self.tip_chord = 0.0
        self.root_yscale = 1.0
        self.tip_yscale = 1.0
        self.span = 30.0
        self.twist = 0.0
        self.sweep = 0.0 # angle @ 25% chord line, in degrees 

        # structural components
        self.steps = 10
        self.leading_edge_diamond = 0.0

        # generated parts
        self.right_ribs = []
        self.left_ribs = []

    def load_airfoils(self, root, tip = None):
        self.root = airfoil.Airfoil(root, 1000, True)
        if tip:
            self.tip = airfoil.Airfoil(tip, 1000, True)

    def make_rib(self, airfoil, chord, lat_dist, twist, label ):
        result = Rib()
        result.contour = copy.deepcopy(airfoil)
        # scale and position
        result.contour.scale(chord, chord)
        result.contour.fit(500, 0.002)
        result.contour.move(-0.25*chord, 0.0)
        # add label (before rotate)
        posx = 0.0
        ty = result.contour.simple_interp(result.contour.top, posx)
        by = result.contour.simple_interp(result.contour.bottom, posx)
        posy = by + (ty - by) / 2.0
        result.contour.add_label( posx, posy, 14, 0, label )
        # do rotate
        result.contour.rotate(twist)
        # compute plan position
        sweep_offset = math.fabs(lat_dist) * math.tan(math.radians(self.sweep))
        #print self.sweep
        #print sweep_offset
        #result.contour.move(sweep_offset, 0.0)
        #print result.contour.get_bounds()
        result.pos = (lat_dist, sweep_offset, 0.0)
        result.sweep = self.sweep

        # leading edge cutout
        diamond = self.leading_edge_diamond
        if diamond > 0.01:
            result.contour.cutout_leading_edge_diamond(diamond)

        return result

    def build(self):
        if self.steps <= 0:
            return
        dp = 1.0 / self.steps
        for p in range(0, self.steps+1):
            print p

            percent = p * dp

            # generate airfoil
            if not self.tip:
                af = self.root
            else:
                af = airfoil.blend(self.root, self.tip, percent)

            # compute rib chord
            if self.tip_chord < 0.01:
                chord = self.root_chord
            else:
                chord = self.root_chord*(1.0-percent) + self.tip_chord*percent

            # compute placement parameters
            lat_dist = self.span * percent
            twist = self.twist * percent

            # make the ribs
            label = 'WR' + str(p+1) 
            right_rib = self.make_rib(af, chord, lat_dist, twist, label)
            self.right_ribs.append(right_rib)

            label = 'WL' + str(p+1)
            left_rib = self.make_rib(af, chord, -lat_dist, twist, label)
            self.left_ribs.append(left_rib)

    def layout_parts_sheets(self, basename, width, height, margin = 0.1):
        l = layout.Layout( basename + '-wing-sheet', width, height, margin )
        for rib in self.right_ribs:
            rib.placed = l.draw_part_cut_line(rib.contour)
        for rib in self.left_ribs:
            rib.placed = l.draw_part_cut_line(rib.contour)
        l.save()

    def layout_parts_templates(self, basename, width, height, margin = 0.1):
        l = layout.Layout( basename + '-wing-template', width, height, margin )
        for rib in self.right_ribs:
            contour = copy.deepcopy(rib.contour)
            contour.rotate(90)
            rib.placed = l.draw_part_demo(contour)
        for rib in self.left_ribs:
            contour = copy.deepcopy(rib.contour)
            contour.rotate(90)
            rib.placed = l.draw_part_demo(contour)
        l.save()

    def layout_plans(self, basename, width, height, margin = 0.1, units = "in", dpi = 90):
        sheet = layout.Sheet( basename + '-wing', width, height )
        yoffset = (height - self.span) * 0.5
        #print yoffset

        # determine "x" extent of ribs
        minx = 0
        maxx = 0
        for rib in self.right_ribs:
            sweep_offset = rib.pos[1]
            # print "sweep offset = " + str(sweep_offset)
            bounds = rib.contour.get_bounds()
            if bounds[0][0] + sweep_offset < minx:
                minx = bounds[0][0] + sweep_offset
            if bounds[1][0] + sweep_offset > maxx:
                maxx = bounds[1][0] + sweep_offset
        #print (minx, maxx)
        dx = maxx - minx
        xmargin = (width - 2*dx) / 3.0
        # print "xmargin = " + str(xmargin)

        # right wing
        planoffset = (xmargin - minx, height - yoffset, -1)
        #print planoffset
        for rib in self.right_ribs:
            rib.placed = sheet.draw_part_top(planoffset, rib.contour, rib.pos, "1px", "red")

        # left wing
        planoffset = ((width - xmargin) - dx - minx, yoffset, 1)
        #print planoffset
        for rib in self.left_ribs:
            rib.placed = sheet.draw_part_top(planoffset, rib.contour, rib.pos, "1px", "red")
        sheet.save()

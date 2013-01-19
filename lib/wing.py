#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy
import math
import svgwrite

import airfoil
import contour
import layout
import spline


class Rib:
    def __init__(self):
        self.thickness = 0.0625
        self.material = "balsa"
        self.contour = None
        self.pos = (0.0, 0.0, 0.0)
        self.placed = False


class Wing:

    def __init__(self):
        self.units = "in"

        # wing layout
        self.root = None        # Airfoil()
        self.tip = None         # Airfoil()
        self.root_yscale = 1.0
        self.tip_yscale = 1.0
        self.span = 0.0
        self.twist = 0.0
        self.stations = []      # 1D array of rib positions
        self.sweep = None       # Contour()
        self.taper = None       # Contour()

        # structural components
        self.steps = 10
        self.leading_edge_diamond = 0.0
        self.trailing_edge_w = 0.0
        self.trailing_edge_h = 0.0
        self.trailing_edge_shape = "flat"
        self.stringers = []
        self.spars = []

        # generated parts
        self.right_ribs = []
        self.left_ribs = []

    def load_airfoils(self, root, tip = None):
        self.root = airfoil.Airfoil(root, 1000, True)
        if tip:
            self.tip = airfoil.Airfoil(tip, 1000, True)

    # define the rib 'stations' as evenly spaced
    def set_num_stations(self, count):
        if count <= 0:
            print "Must specify a number of stations > 0"
            return
        if self.span < 0.01:
            print "Must set wing.span value before computing stations"
            return
        dp = 1.0 / count
        for p in range(0, count+1):
            print p
            percent = p * dp
            lat_dist = self.span * percent
            self.stations.append( lat_dist )

    # define the rib 'stations' as evenly spaced
    def set_stations(self, stations):
        if len(stations) < 2:
            print "Must specify a list of at least 2 station positions"
            return
        self.stations = stations

    # accept an array of station positions
    def set_sweep_angle(self, angle):
        if self.span < 0.01:
            print "Must set wing.span value before sweep angle"
            return
        tip_offset = self.span * math.tan(math.radians(angle))
        self.sweep = contour.Contour()
        self.sweep.top.append( (0.0, 0.0) )
        self.sweep.top.append( (self.span, tip_offset) )

    # define a sweep reference contour (plotted along 25% chord).  It is
    # up to the calling function to make sure the first and last
    # coordinates match up with the root and tip measurements of the wing
    # curve is a list of point pair ( (x1, y1), (x2, y2) .... )
    def set_sweep_curve(self, curve):
        if self.span < 0.01:
            print "Must set wing.span value before sweep curve"
            return
        self.sweep = contour.Contour()
        self.sweep.top = curve

    # define the wing chord (or optionally a separate tip chord for
    # linear taper)
    def set_chord(self, root_chord, tip_chord = 0.0):
        if self.span < 0.01:
            print "Must set wing.span value before chord"
            return
        self.taper = contour.Contour()
        self.taper.top.append( (0.0, root_chord) )
        if tip_chord < 0.1:
            self.taper.top.append( (self.span ,root_chord) )
        else:
            self.taper.top.append( (self.span ,tip_chord) )

    def set_taper_curve(self, curve):
        if self.span < 0.01:
            print "Must set wing.span value before taper curve"
            return
        self.taper = contour.Contour()
        self.taper.top = curve

    def add_stringer(self, side="top", orientation="tangent", \
                         percent=-0.1, front_rel=-0.1, rear_rel=-0.1, \
                         xsize = 0, ysize = 0):
        self.stringers.append( (side, orientation, percent, front_rel, \
                                    rear_rel, xsize, ysize) )

    def add_spar(self, side="top", orientation="vertical", \
                     percent=-0.1, front_rel=-0.1, rear_rel=-0.1, \
                     xsize = 0, ysize = 0):
        self.spars.append( (side, orientation, percent, front_rel, \
                                    rear_rel, xsize, ysize) )

    def make_rib(self, airfoil, chord, lat_dist, sweep_dist, twist, label ):
        result = Rib()
        result.contour = copy.deepcopy(airfoil)

        # scale and position
        result.contour.scale(chord, chord)
        result.contour.fit(500, 0.002)
        result.contour.move(-0.30*chord, 0.0)
        result.contour.save_bounds()

        # add label (before rotate)
        posx = 0.0
        ty = result.contour.simple_interp(result.contour.top, posx)
        by = result.contour.simple_interp(result.contour.bottom, posx)
        posy = by + (ty - by) / 2.0
        result.contour.add_label( posx, posy, 14, 0, label )

        # leading edge cutout
        diamond = self.leading_edge_diamond
        if diamond > 0.01:
            result.contour.cutout_leading_edge_diamond(diamond)

        # cutout stringers (before twist)
        for stringer in self.stringers:
            result.contour.cutout_stringer( stringer[0], stringer[1], \
                                                stringer[2], stringer[3], \
                                                stringer[4], stringer[5], \
                                                stringer[6] )

        # trailing edge cutout
        if self.trailing_edge_w > 0.01 and self.trailing_edge_h > 0.01:
            result.contour.cutout_trailing_edge( self.trailing_edge_w, \
                                                     self.trailing_edge_h, \
                                                     self.trailing_edge_shape )

        # do rotate
        result.contour.rotate(twist)

        # cutout spars (stringer cut after twist)
        for spar in self.spars:
            result.contour.cutout_stringer( spar[0], spar[1], spar[2], \
                                                spar[3], spar[4], spar[5], \
                                                spar[6] )

        # set plan position
        result.pos = (lat_dist, sweep_dist, 0.0)

        return result

    def build(self):
        if len(self.stations) < 2:
            print "Must define at least 2 stations to build a wing"
            return

        sweep_y2 = spline.derivative2( self.sweep.top )
        taper_y2 = spline.derivative2( self.taper.top )

        for index, station in enumerate(self.stations):
            percent = station / self.span

            # generate airfoil
            if not self.tip:
                af = self.root
            else:
                af = airfoil.blend(self.root, self.tip, percent)

            # compute placement parameters
            lat_dist = station
            twist = self.twist * percent

            # compute chord
            if self.taper:
                index = spline.binsearch(self.taper.top, lat_dist)
                chord = spline.spline(self.taper.top, taper_y2, index, lat_dist)
            else:
                print "Cannot build a wing with no chord defined!"
                return

            # compute sweep offset pos if a sweep function provided
            if self.sweep:
                index = spline.binsearch(self.sweep.top, lat_dist)
                sweep_dist = spline.spline(self.sweep.top, sweep_y2, index, \
                                               lat_dist)
            else:
                sweep_dist = 0.0

            # make the ribs
            label = 'WR' + str(index+1) 
            right_rib = self.make_rib(af, chord, lat_dist, sweep_dist, twist, label)
            self.right_ribs.append(right_rib)

            label = 'WL' + str(index+1)
            left_rib = self.make_rib(af, chord, -lat_dist, sweep_dist, twist, label)
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

    # make portion from half tip of cutout forward to ideal airfoil
    # nose
    def make_leading_edge1(self, ribs):
        side1 = []
        side2 = []
        for rib in ribs:
            idealfront = rib.contour.saved_bounds[0][0]
            cutbounds = rib.contour.get_bounds()
            cutfront = cutbounds[0][0]
            side1.append( (idealfront+rib.pos[1], -rib.pos[0]) )
            side2.append( (cutfront+rib.pos[1], -rib.pos[0]) )
        side2.reverse()
        shape = side1 + side2
        return shape

    # make portion from tip of rib cutout to rear of diamond
    def make_leading_edge2(self, ribs):
        side1 = []
        side2 = []
        le = self.leading_edge_diamond
        w = math.sqrt(le*le + le*le)
        halfwidth = w * 0.5
        for rib in ribs:
            cutbounds = rib.contour.get_bounds()
            cutfront = cutbounds[0][0]
            side1.append( (cutfront+rib.pos[1], -rib.pos[0]) )
            side2.append( (cutfront+halfwidth+rib.pos[1], -rib.pos[0]) )
        side2.reverse()
        shape = side1 + side2
        return shape

    def make_trailing_edge(self, ribs):
        side1 = []
        side2 = []
        for rib in ribs:
            idealtip = rib.contour.saved_bounds[1][0]
            cutbounds = rib.contour.get_bounds()
            cuttip = cutbounds[1][0]
            side1.append( (cuttip+rib.pos[1], -rib.pos[0]) )
            side2.append( (idealtip+rib.pos[1], -rib.pos[0]) )
        side2.reverse()
        shape = side1 + side2
        return shape

    def make_stringer(self, stringer, ribs):
        side1 = []
        side2 = []
        halfwidth = stringer[5] * 0.5
        for rib in ribs:
            #print "%=" + str(stringer[2]) + " rf=" + str(stringer[3]) + \
            #    " rr=" + str(stringer[4])
            xpos = rib.contour.get_xpos(stringer[2], stringer[3], stringer[4])
            side1.append( (xpos-halfwidth+rib.pos[1], -rib.pos[0]) )
            side2.append( (xpos+halfwidth+rib.pos[1], -rib.pos[0]) )
        side2.reverse()
        shape = side1 + side2
        return shape

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
            bounds = rib.contour.saved_bounds
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
        for index, rib in enumerate(self.right_ribs):
            if index == 0:
                nudge = -rib.thickness * 0.5
            elif index == len(self.right_ribs) - 1:
                nudge = rib.thickness * 0.5
            else:
                nudge = 0.0
            rib.placed = sheet.draw_part_top(planoffset, rib.contour, \
                                                 rib.pos, rib.thickness, \
                                                 nudge, "1px", "red")
        shape = self.make_leading_edge1(self.right_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        shape = self.make_leading_edge2(self.right_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        shape = self.make_trailing_edge(self.right_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        for stringer in self.stringers:
            shape = self.make_stringer(stringer, self.right_ribs)
            sheet.draw_shape(planoffset, shape, "1px", "red")
        for spar in self.spars:
            shape = self.make_stringer(spar, self.right_ribs)
            sheet.draw_shape(planoffset, shape, "1px", "red")

        # left wing
        planoffset = ((width - xmargin) - dx - minx, yoffset, 1)
        for index, rib in enumerate(self.left_ribs):
            if index == 0:
                nudge = rib.thickness * 0.5
            elif index == len(self.left_ribs) - 1:
                nudge = -rib.thickness * 0.5
            else:
                nudge = 0.0
            rib.placed = sheet.draw_part_top(planoffset, rib.contour, \
                                                 rib.pos, rib.thickness, \
                                                 nudge, "1px", "red")
        shape = self.make_leading_edge1(self.left_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        shape = self.make_leading_edge2(self.left_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        shape = self.make_trailing_edge(self.left_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        for stringer in self.stringers:
            shape = self.make_stringer(stringer, self.left_ribs)
            sheet.draw_shape(planoffset, shape, "1px", "red")
        for spar in self.spars:
            shape = self.make_stringer(spar, self.left_ribs)
            sheet.draw_shape(planoffset, shape, "1px", "red")

        sheet.save()

#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy
import math
import re

try:
    import svgwrite
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/..'))
    import svgwrite

import ac3d
import airfoil
import contour
import layout
import spline


class Rib:
    def __init__(self):
        self.thickness = 0.0625
        self.material = "balsa"
        self.contour = None
        self.pos = [0.0, 0.0, 0.0]
        self.nudge = 0.0        # left right nudge for drawing top down plans
        self.twist = 0.0
        self.part = "wing"      # wing or flap
        self.has_le = True      # has leading edge
        self.has_te = True      # has trailing edge

    def trim_rear(self, cutpos):
        self.contour.trim(side="top", discard="rear", cutpos=cutpos, station=self.pos[0])
        self.contour.trim(side="bottom", discard="rear", cutpos=cutpos, station=self.pos[0])

    # returns the bottom front location which is hard to compute
    # externally (this can be used by the calling layer to position a
    # boundary stringer.
    def trim_front_wedge(self, cutpos, angle):
        self.contour.trim(side="top", discard="front", cutpos=cutpos, station=self.pos[0])
        wedge_angle = math.radians(90.0-angle)
        wedge_slope = -math.tan(wedge_angle)
        
        tx = self.contour.get_xpos(cutpos, station=self.pos[0])
        ty = self.contour.simple_interp(self.contour.top, tx)

        bx = self.contour.intersect("bottom", (tx, ty), wedge_slope)
        botpos = contour.Cutpos( xpos=bx )
        self.contour.trim(side="bottom", discard="front", cutpos=botpos, station=self.pos[0])
        return bx

    def get_label(self):
        if len(self.contour.labels):
            return self.contour.labels[0][4]
        return "unlabeled"

    def relabel_flap(self):
        bounds = self.contour.get_bounds()
        xcenter = (bounds[0][0] + bounds[1][0]) * 0.5
        ycenter = (bounds[0][1] + bounds[1][1]) * 0.5
        if len(self.contour.labels):
            label = self.contour.labels[0][4]
            label = re.sub('W', 'F', label)
        else:
            label = "unlabeled"
        self.contour.labels = []
        self.contour.add_label( xcenter, ycenter, 14, 0, label )


class Stringer:
    def __init__(self, cutout=None, start_station=None, end_station=None, \
                     part=""):
        self.cutout = cutout
        self.start_station = start_station
        self.end_station = end_station
        self.part = part        # wing or flap


class TrailingEdge:
    def __init__(self, width=0.0, height=0.0, shape="", \
                     start_station=None, end_station=None, part="wing"):
        self.width = width
        self.height = height
        self.shape = shape
        self.start_station = start_station
        self.end_station = end_station
        self.part = part        # wing or flap


class Flap:
    def __init__(self, start_station=None, end_station=None, \
                     pos=None, angle=30.0, edge_stringer_size=None):
        self.start_station = start_station
        self.end_station = end_station
        self.pos = pos
        self.angle = angle      # wedge angle for surface movement clearance
        self.edge_stringer_size = edge_stringer_size
        self.start_bottom_str_pos = None
        self.end_bottom_str_pos = None
        self.bottom_str_slope = 0.0


class Hole:
    def __init__(self, type="simple", pos1=None, pos2=None, \
                     radius=0.0, material_width=None, \
                     start_station=None, end_station=None, \
                     part=""):
        self.type = type
        self.pos1 = pos1
        self.pos2 = pos2
        self.radius = radius
        self.material_width = material_width
        self.start_station = start_station
        self.end_station = end_station
        self.part = part        # wing or flap


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
        self.center = 0.25      # center of sweep/taper/pressure/gravity
        self.sweep = None       # Contour()
        self.taper = None       # Contour()

        # structural components
        self.steps = 10
        self.leading_edge_diamond = 0.0
        self.trailing_edges = []
        self.stringers = []
        self.spars = []
        self.flaps = []
        self.holes = []

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

    # define the rib 'stations' explicitely as an array of locations
    def set_stations(self, stations):
        if len(stations) < 2:
            print "Must specify a list of at least 2 station positions"
            return
        self.stations = stations

    # define a fixed sweep angle
    def set_sweep_angle(self, angle):
        if self.span < 0.01:
            print "Must set wing.span value before sweep angle"
            return
        tip_offset = self.span * math.tan(math.radians(angle))
        self.sweep = contour.Contour()
        self.sweep.top.append( (0.0, 0.0) )
        self.sweep.top.append( (self.span, tip_offset) )

    # define a sweep reference contour (plotted along self.center
    # (often 25%) chord).  It is up to the calling function to make
    # sure the first and last "x" coordinates match up with the root
    # and tip measurements of the wing curve is a list of point pair (
    # (x1, y1), (x2, y2) .... )
    def set_sweep_curve(self, curve):
        self.sweep = contour.Contour()
        self.sweep.top = curve

    # define the wing chord (and optionally a separate tip chord for
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
        self.taper = contour.Contour()
        self.taper.top = curve

    def add_trailing_edge(self, width=0.0, height=0.0, shape="", \
                         start_station=None, end_station=None, part=""):
        te = TrailingEdge( width, height, shape, start_station, end_station, \
                               part )
        self.trailing_edges.append( te )

    def add_stringer(self, side="top", orientation="tangent", \
                         percent=None, front=None, rear=None, xpos=None, \
                         xsize=0.0, ysize=0.0, \
                         start_station=None, end_station=None, part=""):
        cutpos = contour.Cutpos( percent, front, rear, xpos )
        cutout = contour.Cutout( side, orientation, cutpos, xsize, ysize )
        stringer = Stringer( cutout, start_station, end_station, part )
        self.stringers.append( stringer )

    def add_spar(self, side="top", orientation="vertical", \
                     percent=None, front=None, rear=None, xpos=None, \
                     xsize=0.0, ysize=0.0, \
                     start_station=None, end_station=None, part=""):
        cutpos = contour.Cutpos( percent, front, rear, xpos )
        cutout = contour.Cutout( side, orientation, cutpos, xsize, ysize )
        spar = Stringer( cutout, start_station, end_station, part )
        self.spars.append( spar )

    def add_flap(self, start_station=None, end_station=None, \
                     pos=None, type="builtup", angle=30.0, \
                     edge_stringer_size=None):
        flap = Flap( start_station, end_station, pos, angle, \
                         edge_stringer_size )
        self.flaps.append( flap )
        if flap.edge_stringer_size != None:
            #double_width = flap.edge_stringer_size[0] * 2.0
            half_offset = flap.edge_stringer_size[0] * 0.5
            front_pos = copy.deepcopy(pos)
            front_pos.move(-half_offset)
            topcutout = contour.Cutout( side="top", orientation="tangent", \
                                            cutpos=front_pos, \
                                            xsize=flap.edge_stringer_size[0], \
                                            ysize=flap.edge_stringer_size[1] )
            stringer = Stringer( topcutout, start_station, end_station, "wing" )
            self.stringers.append( stringer )

            botcutout = contour.Cutout( side="bottom", orientation="tangent", \
                                            cutpos=front_pos, \
                                            xsize=flap.edge_stringer_size[0], \
                                            ysize=flap.edge_stringer_size[1] )
            stringer = Stringer( botcutout, start_station, end_station, "wing" )
            self.stringers.append( stringer )

            rear_pos = copy.deepcopy(pos)
            rear_pos.move(half_offset)
            topcutout = contour.Cutout( side="top", orientation="tangent", \
                                            cutpos=rear_pos, \
                                            xsize=flap.edge_stringer_size[0], \
                                            ysize=flap.edge_stringer_size[1] )
            stringer = Stringer( topcutout, start_station, end_station, "flap" )
            self.stringers.append( stringer )

            # the final bottom flap stinger is computed later so we
            # can deal more properly with curved/tapered wings,
            # blended airfoils and get the start/end points of the
            # bottom flap front stringer correct.

    def add_simple_hole(self, radius=0.0, pos1=None, \
                            start_station=None, end_station=None, part="wing"):
        hole = Hole( type="simple", radius=radius, pos1=pos1, \
                         start_station=start_station, end_station=end_station,\
                         part=part )
        self.holes.append( hole )

    def add_shaped_hole(self, pos1=None, pos2=None, \
                            material_width=None, radius=0.0,\
                            start_station=None, end_station=None, part="wing"):
        hole = Hole( type="shaped", pos1=pos1, pos2=pos2, \
                         material_width=material_width, radius=radius, \
                         start_station=start_station, end_station=end_station,\
                         part=part )
        self.holes.append( hole )

    # return true of lat_dist is between station1 and station2, inclusive.
    # properly handle cases where station1 or station2 is not defined (meaning
    # all the way to the end.
    def match_station(self, start_dist, end_dist, lat_dist):
        result = True
        abs_lat = math.fabs(lat_dist)
        if start_dist != None:
            if start_dist - abs_lat > 0.01:
                result = False
        if end_dist != None:
            if abs_lat - end_dist > 0.01:
                result = False
        return result
            
    def make_raw_rib(self, airfoil, chord, lat_dist, sweep_dist, twist, label ):
        result = Rib()
        result.contour = copy.deepcopy(airfoil)

        # scale and position
        result.contour.scale(chord, chord)
        result.contour.fit(500, 0.002)
        result.contour.move(-self.center*chord, 0.0)
        result.contour.save_bounds()

        # add label (before rotate)
        posx = 0.0
        ty = result.contour.simple_interp(result.contour.top, posx)
        by = result.contour.simple_interp(result.contour.bottom, posx)
        posy = by + (ty - by) / 2.0
        result.contour.add_label( posx, posy, 14, 0, label )

        # set plan position & twist
        result.pos = [lat_dist, sweep_dist, 0.0]
        result.twist = twist

        return result

    def make_rib_cuts(self, rib ):
        lat_dist = rib.pos[0]
        chord = rib.contour.saved_bounds[1][0] - rib.contour.saved_bounds[0][0]

        # leading edge cutout
        diamond = self.leading_edge_diamond
        if diamond > 0.01 and rib.has_le:
            rib.contour.cutout_leading_edge_diamond(diamond)

        # cutout stringers (before twist)
        for stringer in self.stringers:
            if self.match_station(stringer.start_station, stringer.end_station, lat_dist):
                if rib.part == stringer.part:
                    rib.contour.cutout_stringer( stringer.cutout, rib.pos[0] )

        # trailing edge cutout
        for te in self.trailing_edges:
            if self.match_station(te.start_station, te.end_station, lat_dist):
                if rib.has_te and (rib.part == te.part):
                    rib.contour.cutout_trailing_edge( te.width, te.height, \
                                                          te.shape )

        # hole cutouts
        for hole in self.holes:
            if self.match_station(hole.start_station, hole.end_station, lat_dist):
                if rib.part == hole.part:
                    if hole.type == "simple":
                        xpos = rib.contour.get_xpos(hole.pos1, \
                                                        station=rib.pos[0])
                        ty = rib.contour.simple_interp(rib.contour.top, xpos)
                        by = rib.contour.simple_interp(rib.contour.bottom, xpos)
                        ypos = (ty + by) * 0.5
                        rib.contour.cut_hole( xpos, ypos, hole.radius )
                    elif hole.type == "shaped":
                        print "make shaped hole"
                        rib.contour.carve_shaped_hole( pos1=hole.pos1,\
                                          pos2=hole.pos2, \
                                          material_width=hole.material_width, \
                                          radius=hole.radius )


        # do rotate
        rib.contour.rotate(rib.twist)

        print "before spar cutout"
        # cutout spars (stringer cut after twist)
        for spar in self.spars:
            if self.match_station(spar.start_station, spar.end_station, lat_dist):
                print "spar cut match station"
                print "ribpart=" + str(rib.part) + " spar part=" + str(spar.part)
                if rib.part == spar.part:
                    print "cutting a spar: " + str(spar)
                    rib.contour.cutout_stringer( spar.cutout )

    def build(self):
        if len(self.stations) < 2:
            print "Must define at least 2 stations to build a wing"
            return

        sweep_y2 = spline.derivative2( self.sweep.top )
        taper_y2 = spline.derivative2( self.taper.top )

        # make the base ribs at each defined station
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
                sp_index = spline.binsearch(self.taper.top, lat_dist)
                chord = spline.spline(self.taper.top, taper_y2, sp_index, lat_dist)
            else:
                print "Cannot build a wing with no chord defined!"
                return

            print "building station @ " + str(lat_dist) \
                + " chord = " + str(chord)

            # compute sweep offset pos if a sweep function provided
            if self.sweep:
                sw_index = spline.binsearch(self.sweep.top, lat_dist)
                sweep_dist = spline.spline(self.sweep.top, sweep_y2, sw_index, \
                                               lat_dist)
            else:
                sweep_dist = 0.0

            # make the rib (cutouts will be handled later)
            label = 'WR' + str(index+1) 
            right_rib = self.make_raw_rib(af, chord, lat_dist, sweep_dist, \
                                              twist, label)
            if percent < 0.001:
                right_rib.nudge = -right_rib.thickness * 0.5
            elif percent > 0.999:
                right_rib.nudge = right_rib.thickness * 0.5
            self.right_ribs.append(right_rib)

            label = 'WL' + str(index+1)
            left_rib = self.make_raw_rib(af, chord, -lat_dist, sweep_dist, \
                                             twist, label)
            if percent < 0.001:
                left_rib.nudge = right_rib.thickness * 0.5
            elif percent > 0.999:
                left_rib.nudge = -right_rib.thickness * 0.5
            self.left_ribs.append(left_rib)

        # make the control surface ribs.  Instead of dividing the
        # original base ribs into two parts, we make copies of the
        # base ribs and then trim off the parts we don't want.  This
        # makes a bit of sense considering we need double ribs at the
        # cutout edges.  We do this in one pass per side, stepping
        # through each rib and seeing if it matches a control surface
        # cutout and if it's an inner, outer, or mid rib.
        new_ribs = []
        for rib in self.right_ribs:
            for flap in self.flaps:
                if self.match_station(flap.start_station, flap.start_station, rib.pos[0]):
                    #print "start station = " + str(rib.pos[0])
                    newrib = copy.deepcopy(rib)
                    rib.nudge = rib.thickness * 0.5
                    newrib.nudge = -rib.thickness * 1.0
                    flap.start_bot_str_pos = newrib.trim_front_wedge(flap.pos, flap.angle)
                    newrib.part = "flap"
                    newrib.has_le = False
                    new_ribs.append(newrib)
                elif self.match_station(flap.end_station, flap.end_station, rib.pos[0]):
                    #print "end station = " + str(rib.pos[0])
                    newrib = copy.deepcopy(rib)
                    rib.nudge = -rib.thickness * 0.5
                    newrib.nudge = rib.thickness * 1.0
                    flap.end_bot_str_pos = newrib.trim_front_wedge(flap.pos, flap.angle)
                    newrib.part = "flap"
                    newrib.has_le = False
                    new_ribs.append(newrib)
                elif self.match_station(flap.start_station, flap.end_station, rib.pos[0]):
                    #print "match flap at mid station " + str(rib.pos[0])
                    newrib = copy.deepcopy(rib)
                    newrib.trim_front_wedge(flap.pos, flap.angle)
                    newrib.part = "flap"
                    newrib.has_le = False
                    new_ribs.append(newrib)
                    rib.trim_rear(flap.pos)
                    rib.has_te = False

        for rib in new_ribs:
            self.right_ribs.append(rib)

        new_ribs = []
        for rib in self.left_ribs:
            for flap in self.flaps:
                if self.match_station(flap.start_station, flap.start_station, rib.pos[0]):
                    #print "start station = " + str(rib.pos[0])
                    newrib = copy.deepcopy(rib)
                    rib.nudge = -rib.thickness * 0.5
                    newrib.nudge = rib.thickness * 1.0
                    newrib.trim_front_wedge(flap.pos, flap.angle)
                    newrib.part = "flap"
                    newrib.has_le = False
                    new_ribs.append(newrib)
                elif self.match_station(flap.end_station, flap.end_station, rib.pos[0]):
                    #print "end station = " + str(rib.pos[0])
                    newrib = copy.deepcopy(rib)
                    rib.nudge = rib.thickness * 0.5
                    newrib.nudge = -rib.thickness * 1.0
                    newrib.trim_front_wedge(flap.pos, flap.angle)
                    newrib.part = "flap"
                    newrib.has_le = False
                    new_ribs.append(newrib)
                elif self.match_station(flap.start_station, flap.end_station, rib.pos[0]):
                    #print "left match flap at station " + str(rib.pos[0])
                    newrib = copy.deepcopy(rib)
                    newrib.trim_front_wedge(flap.pos, flap.angle)
                    newrib.part = "flap"
                    newrib.has_le = False
                    new_ribs.append(newrib)
                    rib.trim_rear(flap.pos)
                    rib.has_te = False
                    #rib.contour.trim(side="top", discard="rear", cutpos=flap.pos)
                    #rib.contour.trim(side="bottom", discard="rear", cutpos=flap.pos)
        for rib in new_ribs:
            self.left_ribs.append(rib)

        # now place the leading edge bottom stringer for each flap.
        # This is left until now because this can be very dynamic
        # depending on the wing layout and control surface blending.
        for flap in self.flaps:
            if flap.start_bot_str_pos != None and flap.end_bot_str_pos != None \
                    and flap.edge_stringer_size != None:
                xdist = flap.end_station - flap.start_station
                if xdist > 0.0001:
                    ydist = flap.end_bot_str_pos - flap.start_bot_str_pos
                    slope = ydist / xdist
                    half_offset = flap.edge_stringer_size[0] * 0.5
                    cutpos = contour.Cutpos(xpos=flap.start_bot_str_pos, \
                                                atstation=flap.start_station, \
                                                slope=slope)
                    cutpos.move(half_offset)
                    cutout = contour.Cutout(side="bottom", \
                                                orientation="tangent", \
                                                cutpos=cutpos, \
                                                xsize=flap.edge_stringer_size[0], \
                                                ysize=flap.edge_stringer_size[1] )
                    stringer = Stringer( cutout, flap.start_station, flap.end_station, "flap" )
                    self.stringers.append( stringer )

        # do all the cutouts now at the end after we've made and
        # positioned all the ribs for the wing and the control
        # surfaces
        for rib in self.right_ribs:
            self.make_rib_cuts(rib)
        for rib in self.left_ribs:
            self.make_rib_cuts(rib)            

        # a quick pass to update labels on "flap" parts after the
        # cutouts so there is half a chance the label ends up on the
        # part itself
        for rib in self.right_ribs:
            if rib.part == "flap":
                rib.relabel_flap()
        for rib in self.left_ribs:
            if rib.part == "flap":
                rib.relabel_flap()

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
            if rib.has_le:
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
            if rib.has_le:
                cutbounds = rib.contour.get_bounds()
                cutfront = cutbounds[0][0]
                side1.append( (cutfront+rib.pos[1], -rib.pos[0]) )
                side2.append( (cutfront+halfwidth+rib.pos[1], -rib.pos[0]) )
        side2.reverse()
        shape = side1 + side2
        return shape

    def make_trailing_edge(self, te, ribs):
        side1 = []
        side2 = []
        for rib in ribs:
            if self.match_station(te.start_station, te.end_station, rib.pos[0]):
                if rib.part == te.part:
                    if rib.has_te:
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
        halfwidth = stringer.cutout.xsize * 0.5
        for rib in ribs:
            if self.match_station(stringer.start_station, stringer.end_station, rib.pos[0]):
                if rib.part == stringer.part:
                    xpos = rib.contour.get_xpos(stringer.cutout.cutpos, rib.pos[0])
                    side1.append( (xpos-halfwidth+rib.pos[1], -rib.pos[0]+rib.nudge) )
                    side2.append( (xpos+halfwidth+rib.pos[1], -rib.pos[0]+rib.nudge) )
        side2.reverse()
        shape = side1 + side2

        if len(shape) < 4:
            print "error, made a bad shape!"

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
            rib.placed = sheet.draw_part_top(planoffset, rib.contour, \
                                                 rib.pos, rib.thickness, \
                                                 rib.nudge, "1px", "red")
        shape = self.make_leading_edge1(self.right_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        shape = self.make_leading_edge2(self.right_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        for te in self.trailing_edges:
            shape = self.make_trailing_edge(te, self.right_ribs)
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
            rib.placed = sheet.draw_part_top(planoffset, rib.contour, \
                                                 rib.pos, rib.thickness, \
                                                 rib.nudge, "1px", "red")
        shape = self.make_leading_edge1(self.left_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        shape = self.make_leading_edge2(self.left_ribs)
        sheet.draw_shape(planoffset, shape, "1px", "red")
        for te in self.trailing_edges:
            shape = self.make_trailing_edge(te, self.left_ribs)
            sheet.draw_shape(planoffset, shape, "1px", "red")
        for stringer in self.stringers:
            shape = self.make_stringer(stringer, self.left_ribs)
            sheet.draw_shape(planoffset, shape, "1px", "red")
        for spar in self.spars:
            shape = self.make_stringer(spar, self.left_ribs)
            sheet.draw_shape(planoffset, shape, "1px", "red")

        sheet.save()

    def build_ac3d(self, basename):
        ac = ac3d.AC3D(basename)
        ac.gen_headers("wing", 2)
        # right wing
        ac.start_object_group("right wing", len(self.right_ribs))
        for rib in self.right_ribs:
            ac.make_object_poly("wing rib", rib.contour.poly, rib.thickness, rib.pos)
        # left wing
        ac.start_object_group("left wing", len(self.left_ribs))
        for rib in self.left_ribs:
            ac.make_object_poly("wing rib", rib.contour.poly, rib.thickness, rib.pos)

        shape = self.make_leading_edge1(self.right_ribs)
        #sheet.draw_shape(planoffset, shape, "1px", "red")
        shape = self.make_leading_edge2(self.right_ribs)
        #sheet.draw_shape(planoffset, shape, "1px", "red")
        for te in self.trailing_edges:
            shape = self.make_trailing_edge(te, self.right_ribs)
            #sheet.draw_shape(planoffset, shape, "1px", "red")
        for stringer in self.stringers:
            shape = self.make_stringer(stringer, self.right_ribs)
            #sheet.draw_shape(planoffset, shape, "1px", "red")
        for spar in self.spars:
            shape = self.make_stringer(spar, self.right_ribs)
            #sheet.draw_shape(planoffset, shape, "1px", "red")
        ac.end_object_group()
        ac.close()

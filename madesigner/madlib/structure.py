# structure.py - a generic high level structure
#
# Copyright (C) 2013-2017 - Curtis Olson, curtolson@flightgear.org
# http://madesigner.flightgear.org

import copy
import math
import numpy as np
import re
import sys, os

import Polygon
import Polygon.Utils
import svgwrite

from . import ac3d
from . import airfoil
from . import contour
from . import freecad
from . import layout

# path to your FreeCAD.so or FreeCAD.dll file
FREECADPATH = '/usr/lib64/freecad/lib'
sys.path.append(FREECADPATH)
import FreeCAD
import Part
from FreeCAD import Base

# rotate a point about (xdist, 0)
def rotate_point( pt, xdist, angle ):
    rad = math.radians(angle)
    newx = (pt[0]-xdist) * math.cos(rad) - pt[2] * math.sin(rad) + xdist
    newy = pt[1]
    newz = pt[2] * math.cos(rad) + (pt[0]-xdist) * math.sin(rad)
    return [newx, newy, newz]

def rotate( points, xdist, angle ):
    newpoints = []
    for pt in points:
        print(pt)
        newpoints.append( rotate_point(pt, xdist, angle) )
    return newpoints


class TrailingEdge:
    def __init__(self, width=0.0, height=0.0, shape="", \
                     start_station=None, end_station=None, part=""):
        self.width = width
        self.height = height
        self.shape = shape
        self.start_station = start_station
        self.end_station = end_station
        self.part = part        # wing or flap
        self.side = "right"
        self.points = []


class LeadingEdge:
    def __init__(self, size=None, start_station=None, end_station=None, \
                     part=""):
        self.size = size
        self.start_station = start_station
        self.end_station = end_station
        self.part = part        # wing or flap
        self.side = "right"
        self.points = []


class Sheeting:
    def __init__(self, surf="top", xstart=0.0, xend=None, xdist=None, \
                     ysize=0.0, start_station=None, end_station=None, part=""):
        self.surf = surf
        self.xstart = xstart
        self.xend = xend
        self.xdist = xdist
        self.ysize = ysize
        self.start_station = start_station
        self.end_station = end_station
        self.part = part
        self.side = "right"
        self.top_points = []
        self.bot_points = []


class Stringer:
    def __init__(self, cutout=None, start_station=None, end_station=None, \
                     part=""):
        self.cutout = cutout
        self.start_station = start_station
        self.end_station = end_station
        self.part = part        # wing or flap
        self.side = "right"
        self.points = []


class Hole:
    def __init__(self, type="simple", pos1=None, pos2=None, \
                     style="Radius", size=0.0, material_width=None, \
                     start_station=None, end_station=None, \
                     part=""):
        self.type = type
        self.pos1 = pos1
        self.pos2 = pos2
        self.style = style
        self.size = size
        self.material_width = material_width
        self.start_station = start_station
        self.end_station = end_station
        self.part = part        # wing or flap
        self.side = "right"


class BuildTab:
    def __init__(self, surf="bottom", pos=None, xsize=0.5, ypad=0.0, \
                 start_station=None, end_station=None, \
                 part=""):
        self.surf = surf
        self.pos = pos
        self.xsize = xsize
        self.ypad = ypad
        self.start_station = start_station
        self.end_station = end_station
        self.part = part        # wing or flap
        self.side = "right"
        self.points = []


class Rib:
    def __init__(self):
        self.thickness = 0.0625
        self.material = "balsa"
        self.contour = None
        self.pos = [0.0, 0.0, 0.0]
        self.nudge = 0.0        # left right nudge for drawing top down plans
        self.twist = 0.0
        self.part = "wing"      # wing or flap
        self.side = "right"
        self.type = "middle"
        # todo can we eliminate has_le/has_te by using self.part names?
        self.has_le = True      # has leading edge
        self.has_te = True      # has trailing edge

    # returns the bottom front location which is hard to compute
    # externally (this can be used by the calling layer to position a
    # boundary stringer.
    def find_flap_bottom_front(self, cutpos, angle):
        wedge_angle = math.radians(90.0-angle)
        wedge_slope = -math.tan(wedge_angle)
        
        tx = self.contour.get_xpos(cutpos, station=self.pos[0])
        ty = self.contour.simple_interp(self.contour.top, tx)

        bx = self.contour.intersect("bottom", (tx, ty), wedge_slope)
        return bx

    def trim_rear(self, cutpos):
        self.contour.trim(surf="top", discard="rear", cutpos=cutpos, station=self.pos[0])
        self.contour.trim(surf="bottom", discard="rear", cutpos=cutpos, station=self.pos[0])

    # returns the bottom front location which is hard to compute
    # externally (this can be used by the calling layer to position a
    # boundary stringer.
    def trim_front_wedge(self, cutpos, angle):
        self.contour.trim(surf="top", discard="front", cutpos=cutpos, station=self.pos[0])
        bx = self.find_flap_bottom_front(cutpos, angle)
        botpos = contour.Cutpos( xpos=bx )
        self.contour.trim(surf="bottom", discard="front", cutpos=botpos, station=self.pos[0])
        return bx

    # segment line: divide line in half and leave a small bit uncut in
    # middle and ends
    def segment_line(self, p1, p2):
        solid_len = 0.1
        print("segment line")
        p1 = np.array(p1)
        p2 = np.array(p2)
        vector = p2 - p1
        dist = np.linalg.norm(vector)
        if dist > solid_len*3:
            d2 = dist / 2.0
            np1 = p1 + vector * solid_len / dist
            np2 = p1 + vector * (d2 - solid_len*0.5) / dist
            np3 = p1 + vector * (d2 + solid_len*0.5) / dist
            np4 = p1 + vector * (dist - solid_len) / dist
            return [np1, np2, np3, np4]
        else:
            return [p1, p2]        
        
    # instead of trimming, add cut lines so the part is intact, but
    # can be separated easily after the structure is assembled.
    def add_wedge_cut_lines(self, cutpos, angle):
        # hinge point (top)
        tx = self.contour.get_xpos(cutpos, station=self.pos[0])
        ty = self.contour.simple_interp(self.contour.top, tx)

        # bottom front of wedge (directly below hinge line)
        bfy = self.contour.simple_interp(self.contour.bottom, tx)
        
        # bottom rear of wedge (front of flap on the bottom)
        brx = self.find_flap_bottom_front(cutpos, angle)
        bry = self.contour.simple_interp(self.contour.bottom, brx)

        front = self.segment_line([tx, ty], [tx, bfy]) # front of wedge
        rear = self.segment_line([tx, ty], [brx, bry]) # rear of wedge
        
        # list of line pairs
        lines = []
        for p in front:
            lines.append( [p[0], 0.0, p[1]] )
        for p in rear:
            lines.append( [p[0], 0.0, p[1]] )
        print("lines:", lines)
        print("rotating about:", 0.0)
        self.contour.cut_lines = rotate(lines, 0.0, self.twist)
        print("rotated lines:", self.contour.cut_lines)
        
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

    def hull_area(self):
        if self.contour.poly == None:
            self.contour.make_poly()
        hull = Polygon.Utils.convexHull(self.contour.poly)
        return hull.area()


class Structure:

    def __init__(self, basename):
        self.basename = basename
        self.units = "in"

        # wing layout
        self.name = "none"
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
        self.dihedral = 0.0

        # structural components
        self.steps = 10
        self.leading_edges = []
        self.trailing_edges = []
        self.sheeting = []
        self.stringers = []
        self.spars = []
        self.holes = []
        self.build_tabs = []

        # generated parts
        self.right_ribs = []
        self.left_ribs = []

        # build parameters
        self.airfoil_samples = 50 # 50 = fast, 100 = mid, 1000 = quality
        self.circle_points = 8    # 8 = fast, 16 = mid, 32 = quality

    def load_airfoils(self, root, tip=None):
        self.root = airfoil.Airfoil(root, self.airfoil_samples, True)
        if tip:
            self.tip = airfoil.Airfoil(tip, self.airfoil_samples, True)

    # define the rib 'stations' as evenly spaced
    def set_num_stations(self, count):
        if count <= 0:
            print("Must specify a number of stations > 0")
            return
        if self.span < 0.01:
            print("Must set wing.span value before computing stations")
            return
        dp = 1.0 / count
        for p in range(0, count+1):
            print(p)
            percent = p * dp
            lat_dist = self.span * percent
            self.stations.append( lat_dist )

    # define the rib 'stations' explicitely as an array of locations
    def set_stations(self, stations):
        if len(stations) < 2:
            print("Must specify a list of at least 2 station positions")
            return
        self.stations = stations

    # define a fixed sweep angle
    def set_sweep_angle(self, angle):
        if self.span < 0.01:
            print("Must set wing.span value before sweep angle")
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
            print("Must set wing.span before calling set_chord()")
            return
        if len(self.stations) < 2:
            print("Must create stations() before calling set_chord()")
            return
        start_station = self.stations[0]
        end_station = self.stations[len(self.stations)-1]
        self.taper = contour.Contour()
        self.taper.top.append( (start_station, root_chord) )
        if tip_chord < 0.1:
            self.taper.top.append( (end_station, root_chord) )
        else:
            self.taper.top.append( (end_station, tip_chord) )

    def set_taper_curve(self, curve):
        self.taper = contour.Contour()
        self.taper.top = curve

    def add_trailing_edge(self, width=0.0, height=0.0, shape="", \
                              start_station=None, end_station=None, \
                              mirror=True, part=""):
        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]
        te = TrailingEdge( width, height, shape, \
                               start_station, end_station, part )
        te.side = "right"
        self.trailing_edges.append( te )
        if mirror:
            te = TrailingEdge( width, height, shape, \
                                   -start_station, -end_station, part )
            te.side = "left"
            self.trailing_edges.append( te )

    def add_leading_edge(self, size=0.0, \
                             start_station=None, end_station=None, \
                             mirror=True, part=""):
        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]
        le = LeadingEdge( size, start_station, end_station, \
                               part )
        le.side = "right"
        self.leading_edges.append( le )
        if mirror:
            le = LeadingEdge( size, -start_station, -end_station, \
                               part )
            le.side = "left"
            self.leading_edges.append( le )

    def add_sheeting(self, surf="top", xstart=0.0, xend=None, xdist=None, \
                         ysize=0.0,
                         start_station=None, end_station=None, mirror=True, \
                         part=""):
        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]
        sheet = Sheeting( surf, xstart, xend, xdist, ysize, start_station, end_station, part )
        sheet.side = "right"
        self.sheeting.append( sheet )
        if mirror:
            sheet = Sheeting( surf, xstart, xend, xdist, ysize, -start_station, -end_station, part )
            sheet.side = "left"
            self.sheeting.append( sheet )

    def add_stringer(self, surf="top", orientation="tangent", \
                         percent=None, front=None, rear=None, xpos=None, \
                         xsize=0.0, ysize=0.0, \
                         start_station=None, end_station=None, mirror=True, \
                         part=""):
        cutpos = contour.Cutpos( percent, front, rear, xpos )
        cutout = contour.Cutout( surf, orientation, cutpos, xsize, ysize )
        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]
        stringer = Stringer( cutout, start_station, end_station, part )
        stringer.side = "right"
        self.stringers.append( stringer )
        if mirror:
            stringer = Stringer( cutout, -start_station, -end_station, part )
            stringer.side = "left"
            self.stringers.append( stringer )

    def add_spar(self, surf="top", orientation="vertical", \
                     percent=None, front=None, rear=None, xpos=None, \
                     xsize=0.0, ysize=0.0, \
                     start_station=None, end_station=None, mirror=True, \
                     part=""):
        cutpos = contour.Cutpos( percent, front, rear, xpos )
        cutout = contour.Cutout( surf, orientation, cutpos, xsize, ysize )
        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]
        spar = Stringer( cutout, start_station, end_station, part )
        spar.side = "right"
        self.spars.append( spar )
        if mirror:
            spar = Stringer( cutout, -start_station, -end_station, part )
            spar.side = "left"
            self.spars.append( spar )

    def add_simple_hole(self, style="Radius", size=0.0, pos1=None,
                        start_station=None, end_station=None, mirror=True,
                        part="wing"):
        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]
        hole = Hole( type="simple", style=style, size=size, pos1=pos1,
                     start_station=start_station, end_station=end_station,
                     part=part )
        hole.side = "right"
        self.holes.append( hole )
        if mirror:
            hole = Hole( type="simple", style=style, size=size, pos1=pos1,
                             start_station=-start_station,
                             end_station=-end_station,
                             part=part )
            hole.side = "left"
            self.holes.append( hole )
  

    def add_shaped_hole(self, pos1=None, pos2=None, \
                            material_width=None, radius=0.0,\
                            start_station=None, end_station=None, mirror=True, \
                            part="wing"):
        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]
        hole = Hole( type="shaped", pos1=pos1, pos2=pos2, \
                         material_width=material_width, radius=radius, \
                         start_station=start_station, end_station=end_station,\
                         part=part )
        hole.side = "right"
        self.holes.append( hole )
        if mirror:
            hole = Hole( type="shaped", pos1=pos1, pos2=pos2, \
                             material_width=material_width, radius=radius, \
                             start_station=-start_station, \
                             end_station=-end_station,\
                             part=part )
            hole.side = "left"
            self.holes.append( hole )

    def add_build_tab(self, surf="top", \
                          percent=None, front=None, rear=None, xpos=None, \
                          xsize=0.0, ypad=0.0, \
                          start_station=None, end_station=None, mirror=True, \
                          part=""):
        cutpos = contour.Cutpos( percent, front, rear, xpos )
        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]
        tab = BuildTab( surf, cutpos, xsize, ypad, \
                        start_station, end_station, part )
        tab.side = "right"
        self.build_tabs.append( tab )
        if mirror:
            tab = BuildTab( surf, cutpos, xsize, ypad,
                            -start_station, -end_station, part )
            tab.side = "left"
            self.build_tabs.append( tab )

    # return the tip position of the wing panel after dihedral rotation
    def get_tip_pos(self):
        rad = math.radians(self.dihedral)
        sa = math.sin(rad)
        ca = math.cos(rad)
        newy = self.span * math.cos(rad)
        newz = self.span * math.sin(rad)
        return( 0.0, newy, newz )

    # return true of lat_dist is between station1 and station2, inclusive.
    # properly handle cases where station1 or station2 is not defined (meaning
    # all the way to the end.
    def match_station(self, start_dist, end_dist, lat_dist):
        result = True
        if start_dist > 0.0 or end_dist > 0.0:
            if lat_dist < start_dist or lat_dist > end_dist:
                result = False
        else:
            if lat_dist > start_dist or lat_dist < end_dist:
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

    def make_rib_cuts(self, rib):
        lat_dist = rib.pos[0]
        chord = rib.contour.saved_bounds[1][0] - rib.contour.saved_bounds[0][0]

        # trailing edge cutout (first!)
        for te in self.trailing_edges:
            if self.match_station(te.start_station, te.end_station, lat_dist):
                if rib.has_te and rib.part == te.part and rib.side == te.side:
                    shape = rib.contour.cutout_trailing_edge( width=te.width, height=te.height, shape=te.shape, force_fit=True, pos=rib.pos, nudge=rib.nudge)
                    if len(shape):
                        rot_shape = rotate(shape, rib.pos[1], rib.twist)
                        te.points.append(rot_shape)

        # leading edge cutout
        for le in self.leading_edges:
            if self.match_station(le.start_station, le.end_station, lat_dist):
                if rib.has_le and rib.side == le.side:
                    shape = rib.contour.cutout_leading_edge_diamond( le.size, rib.pos, rib.nudge )
                    if len(shape):
                        rot_shape = rotate(shape, rib.pos[1], rib.twist)
                        le.points.append(rot_shape)
                else:
                    print("no match: " + " or " + rib.side + " != " + le.side + " (has_le= " + str(rib.has_le) + ")")

        # sheeting next
        for sheet in self.sheeting:
            if self.match_station(sheet.start_station, sheet.end_station, lat_dist):
                if rib.part == sheet.part and rib.side == sheet.side:
                    shape = rib.contour.cutout_sweep(surf=sheet.surf, xstart=sheet.xstart, xend=sheet.xend, xdist=sheet.xdist, ysize=sheet.ysize, pos=rib.pos, nudge=rib.nudge)
                    if len(shape) > 1:
                        rot_shape_top = rotate(shape[0], rib.pos[1], rib.twist)
                        rot_shape_bot = rotate(shape[1], rib.pos[1], rib.twist)
                        sheet.top_points.append(rot_shape_top)
                        sheet.bot_points.append(rot_shape_bot)

        # cutout stringers (before twist)
        for stringer in self.stringers:
            if self.match_station(stringer.start_station, stringer.end_station, lat_dist):
                if rib.side != stringer.side:
                    continue
                if rib.part != 'flap' and stringer.part == 'flap':
                    continue
                shape = rib.contour.cutout_stringer(stringer.cutout, rib.pos, rib.nudge)
                if shape != None and len(shape):
                    rot_shape = rotate(shape, rib.pos[1], rib.twist)
                    stringer.points.append(rot_shape)

        # hole cutouts
        for hole in self.holes:
            if self.match_station(hole.start_station, hole.end_station, lat_dist):
                if hole.type == "simple":
                    print('hole:', lat_dist)
                    xpos = rib.contour.get_xpos(hole.pos1,
                                                station=rib.pos[0],
                                                sweep=rib.pos[1])
                    ty = rib.contour.simple_interp(rib.contour.top, xpos)
                    by = rib.contour.simple_interp(rib.contour.bottom, xpos)
                    print('xpos:', xpos, ty, by)
                    if ty == None or by == None:
                        continue
                    ypos = (ty + by) * 0.5
                    if hole.style == 'Radius':
                        radius = hole.size
                    elif hole.style == '% Height':
                        radius = (ty - by) * hole.size * 0.5
                    if radius < 0.0:
                        radius = 0.0
                    print('ok')
                    rib.contour.cut_hole( xpos, ypos, radius,
                                          points=self.circle_points )
                elif hole.type == "shaped":
                    #print "make shaped hole"
                    rib.contour.carve_shaped_hole( pos1=hole.pos1,
                                                   pos2=hole.pos2,
                                                   sweep=rib.pos[1],
                                                   material_width=hole.material_width,
                                                   radius=hole.radius,
                                                   circle_points=self.circle_points )


        # do rotate
        rib.contour.rotate(rib.twist)

        # cutout spars (stringer cut after twist)
        for spar in self.spars:
            if self.match_station(spar.start_station, spar.end_station, lat_dist):
                if rib.side == spar.side:
                    shape = rib.contour.cutout_stringer(spar.cutout, rib.pos, rib.nudge)
                    if len(shape):
                        spar.points.append( shape )

        # add build tabs last (after twist of course)
        for tab in self.build_tabs:
            if self.match_station(tab.start_station, tab.end_station, lat_dist):
                if rib.side == tab.side:
                    shape = rib.contour.add_build_tab(tab.surf, tab.pos, tab.xsize, tab.ypad)

    def layout_parts_sheets(self, width, height, step=None, units="in",
                            speed="fast"):
        l = layout.Layout( self.basename + '-sheet', width, height, step=step, units=units )
        # sort by size (ascending), then place in reverse order (largest first)
        sorted_list = []
        for rib in self.right_ribs:
            sorted_list.append( (rib.hull_area(), rib) )
        for rib in self.left_ribs:
            sorted_list.append( (rib.hull_area(), rib) )
        print("placement_list:", sorted_list)
        sorted_list = sorted(sorted_list, key=lambda fields: fields[0])
        # place the ribs
        for (area, rib) in reversed(sorted_list):
            rib.placed = l.draw_part_cut_line(rib.contour, speed=speed)
        l.save()

    def layout_parts_templates(self, width, height, step=None, speed="fast"):
        l = layout.Layout( self.basename + '-template', width, height, step )
        for rib in self.right_ribs:
            contour = copy.deepcopy(rib.contour)
            contour.rotate(90)
            rib.placed = l.draw_part_demo(contour, speed=speed)
        for rib in self.left_ribs:
            contour = copy.deepcopy(rib.contour)
            contour.rotate(90)
            rib.placed = l.draw_part_demo(contour, speed=speed)
        l.save()

    def make_top_extrusion(self, points, front_half=None, rear_half=None):
        side1 = []
        side2 = []
        for contour in points:
            #print "contour = " + str(contour)
            minx = None
            maxx = None
            station = None
            for pt in contour:
                if minx == None or pt[0] < minx:
                    minx = pt[0]
                if maxx == None or pt[0] > maxx:
                    maxx = pt[0]
                station = pt[1]
            halfway = (minx + maxx) / 2.0
            if front_half:
                side1.append( (minx, -station) )
                side2.append( (halfway, -station) )
            elif rear_half:
                side1.append( (halfway, -station) )
                side2.append( (maxx, -station) )
            else:
                side1.append( (minx, -station) )
                side2.append( (maxx, -station) )
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

        if len(shape) == 0:
            print("wing: made an empty stringer shape")
        elif len(shape) < 4:
            print("wing: made a (bad) stringer shape with only " \
                + str(len(shape)) + " points!")

        return shape

    def layout_plans(self, width, height, step=None, units="in", dpi=90):
        sheet = layout.Sheet( self.basename + "-plan", width=width,
                              height=height, step=step, units=units,
                              dpi=dpi )
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
        planoffset = (xmargin - minx, height - yoffset + self.stations[0], -1)
        for index, rib in enumerate(self.right_ribs):
            rib.placed = sheet.draw_part_top(planoffset, rib.contour, \
                                                 rib.pos, rib.thickness, \
                                                 rib.nudge, "1px", "red")
        for le in self.leading_edges:
            if le.side == "right":
                shape = self.make_top_extrusion(le.points, front_half=True)
                if len(shape):
                    sheet.draw_shape(planoffset, shape, "1px", "red")
            if le.side == "right":
                shape = self.make_top_extrusion(le.points, rear_half=True)
                if len(shape):
                    sheet.draw_shape(planoffset, shape, "1px", "red")
        for te in self.trailing_edges:
            if te.side == "right":
                shape = self.make_top_extrusion(te.points)
                if len(shape):
                    sheet.draw_shape(planoffset, shape, "1px", "red")
        for stringer in self.stringers:
            shape = self.make_stringer(stringer, self.right_ribs)
            if len(shape):
                sheet.draw_shape(planoffset, shape, "1px", "red")
        for spar in self.spars:
            shape = self.make_stringer(spar, self.right_ribs)
            if len(shape):
                sheet.draw_shape(planoffset, shape, "1px", "red")

        # left wing
        planoffset = ((width - xmargin) - dx - minx, yoffset - self.stations[0], 1)
        for index, rib in enumerate(self.left_ribs):
            rib.placed = sheet.draw_part_top(planoffset, rib.contour, \
                                                 rib.pos, rib.thickness, \
                                                 rib.nudge, "1px", "red")
        for le in self.leading_edges:
            if le.side == "left":
                shape = self.make_top_extrusion(le.points, front_half=True)
                if len(shape):
                    sheet.draw_shape(planoffset, shape, "1px", "red")
            if le.side == "left":
                shape = self.make_top_extrusion(le.points, rear_half=True)
                if len(shape):
                    sheet.draw_shape(planoffset, shape, "1px", "red")
        for te in self.trailing_edges:
            if te.side == "left":
                shape = self.make_top_extrusion(te.points)
                if len(shape):
                    sheet.draw_shape(planoffset, shape, "1px", "red")
        for stringer in self.stringers:
            shape = self.make_stringer(stringer, self.left_ribs)
            if len(shape):
                sheet.draw_shape(planoffset, shape, "1px", "red")
        for spar in self.spars:
            shape = self.make_stringer(spar, self.left_ribs)
            if len(shape):
                sheet.draw_shape(planoffset, shape, "1px", "red")

        sheet.save()

    def build_ac3d(self, ac, xoffset=0.0, yoffset=0.0):
        groups = 2              # left & right wings

        m1 = ac.make_rotation_matrix("Z", -90)
        m2 = ac.make_rotation_matrix("Y", -90)
        m = ac.multiply_rotation_matrix(m1, m2)

        ac.start_object_group("wing", groups, m)

        # right wing

        # first count right wing parts
        kids = len(self.right_ribs)
        for te in self.trailing_edges:
            if te.side == "right":
                kids += 1
        for le in self.leading_edges:
            if le.side == "right":
                kids += 1
        for sheet in self.sheeting:
            if sheet.side == "right":
                kids += 1
        for stringer in self.stringers:
            if stringer.side == "right":
                kids += 1
        for spar in self.spars:
            if spar.side == "right":
                kids += 1

        m = ac.make_rotation_matrix("X", self.dihedral)
        loc = (0.0, xoffset, yoffset)
        ac.start_object_group("right wing", kids, m, loc)

        # make parts
        for rib in self.right_ribs:
            ac.make_object_poly("wing rib", rib.contour.poly, rib.thickness, rib.pos, rib.nudge)

        if len(self.trailing_edges):
            for te in self.trailing_edges:
                if te.side == "right":
                    ac.make_extrusion("trailing edge", te.points,
                                      te.side=="left")
        if len(self.leading_edges):
            for le in self.leading_edges:
                if le.side == "right":
                    ac.make_extrusion("leading edge", le.points,
                                      le.side=="left")
        if len(self.sheeting):
            for sheet in self.sheeting:
                if sheet.side == "right":
                    ac.make_sheet("sheet", sheet.top_points, sheet.bot_points,
                                  sheet.side=="left")
        if len(self.stringers):
            for stringer in self.stringers:
                if stringer.side == "right":
                    ac.make_extrusion("stringer", stringer.points,
                                      stringer.side=="left")
        if len(self.spars):
            for spar in self.spars:
                if spar.side == "right":
                    ac.make_extrusion("spar", spar.points, spar.side=="left")
                    
        # left wing

        # first count left wing parts
        kids = len(self.left_ribs)
        for te in self.trailing_edges:
            if te.side == "left":
                kids += 1
        for le in self.leading_edges:
            if le.side == "left":
                kids += 1
        for sheet in self.sheeting:
            if sheet.side == "left":
                kids += 1
        for stringer in self.stringers:
            if stringer.side == "left":
                kids += 1
        for spar in self.spars:
            if spar.side == "left":
                kids += 1

        m = ac.make_rotation_matrix("X", -self.dihedral)
        loc = (0.0, -xoffset, yoffset)
        ac.start_object_group("left wing", kids, m, loc)

        # make parts
        for rib in self.left_ribs:
            ac.make_object_poly("wing rib", rib.contour.poly, rib.thickness, rib.pos, rib.nudge)

        if len(self.trailing_edges):
            for te in self.trailing_edges:
                if te.side == "left":
                    if len(te.points):
                        ac.make_extrusion("trailing edge", te.points,
                                          te.side=="left")
                    else:
                        print("Error: no trailing edge points")
        if len(self.leading_edges):
            for le in self.leading_edges:
                if le.side == "left":
                    ac.make_extrusion("leading edge", le.points,
                                      le.side=="left")
        if len(self.sheeting):
            for sheet in self.sheeting:
                if sheet.side == "left":
                    ac.make_sheet("sheet", sheet.top_points, sheet.bot_points,
                                  sheet.side=="left")
        if len(self.stringers):
            for stringer in self.stringers:
                if stringer.side == "left":
                    if len(stringer.points):
                        ac.make_extrusion("stringer", stringer.points,
                                          stringer.side=="left")
                    else:
                        print("Error: no trailing edge points")
        if len(self.spars):
            for spar in self.spars:
                if spar.side == "left":
                    ac.make_extrusion("spar", spar.points, spar.side=="left")

    def build_freecad(self, doc, xoffset=0.0, yoffset=0.0, twist=0.0):
        doc.make_extra_group('Wing_' + self.name)

        # right_ref = Base.Vector(0, xoffset, yoffset)
        # left_ref = Base.Vector(0, -xoffset, yoffset)
        # right_rot = Base.Rotation(Base.Vector(1, 0, 0), self.dihedral)
        # right_pl = FreeCAD.Placement(right_ref, right_rot)
        # left_rot = Base.Rotation(Base.Vector(1, 0, 0), -self.dihedral)
        # left_pl = FreeCAD.Placement(left_ref, left_rot)
        
        right_m = Base.Matrix()
        right_m.rotateY(math.radians(-twist))
        right_m.rotateX(math.radians(self.dihedral))
        right_m.move(Base.Vector(0, xoffset, yoffset))

        left_m = Base.Matrix()
        left_m.rotateY(math.radians(-twist))
        left_m.rotateX(math.radians(-self.dihedral))
        left_m.move(Base.Vector(0, -xoffset, yoffset))

        left_pl = FreeCAD.Placement(left_m)
        right_pl = FreeCAD.Placement(right_m)
        
        # make parts
        for rib in self.right_ribs:
            part = doc.make_object(rib.contour.poly, rib.thickness, rib.pos, rib.nudge)
            part.Placement = right_pl
            doc.add_object("kit", "rib", part)

        for rib in self.left_ribs:
            part = doc.make_object(rib.contour.poly, rib.thickness, rib.pos, rib.nudge)
            part.Placement = left_pl
            doc.add_object("kit", "rib", part)

        for te in self.trailing_edges:
            if te.side == "left":
                part = doc.make_extrusion("trailing edge", te.points,
                                          te.side=="left")
                part.Placement = left_pl
                doc.add_object('stock', "trailing edge", part)
            if te.side == "right":
                part = doc.make_extrusion("trailing edge", te.points,
                                          te.side=="left")
                part.Placement = right_pl
                doc.add_object('stock', "trailing edge", part)
                
        for le in self.leading_edges:
            if le.side == "left":
                part = doc.make_extrusion("leading edge", le.points,
                                          le.side=="left")
                part.Placement = left_pl
                doc.add_object('stock', "leading edge", part)
            if le.side == "right":
                part = doc.make_extrusion("leading edge", le.points,
                                          le.side=="left")
                part.Placement = right_pl
                doc.add_object('stock', "leading edge", part)
                
        for spar in self.spars:
            if spar.side == "left":
                part = doc.make_extrusion("spar", spar.points,
                                          spar.side=="left")
                part.Placement = left_pl
                doc.add_object('stock', "spar", part)
            if spar.side == "right":
                part = doc.make_extrusion("spar", spar.points,
                                          spar.side=="left")
                part.Placement = right_pl
                doc.add_object('stock', "spar", part)

        for stringer in self.stringers:
            if stringer.side == "left":
                part = doc.make_extrusion("stringer", stringer.points,
                                          stringer.side=="left")
                part.Placement = left_pl
                doc.add_object('stock', "stringer", part)
            if stringer.side == "right":
                part = doc.make_extrusion("stringer", stringer.points,
                                          stringer.side=="left")
                part.Placement = right_pl
                doc.add_object('stock', "stringer", part)


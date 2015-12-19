#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy
import math

import airfoil
import contour
from structure import Structure, Stringer
import spline


class Flap:
    def __init__(self, start_station=None, end_station=None, \
                     pos=None, angle=30.0, edge_stringer_size=None):
        self.start_station = start_station
        self.end_station = end_station
        self.pos = pos
        self.angle = angle      # wedge angle for surface movement clearance
        self.edge_stringer_size = edge_stringer_size
        self.start_bot_str_pos = None
        self.end_bot_str_pos = None
        self.bottom_str_slope = 0.0
        self.side = "right"


class Wing(Structure):

    def __init__(self, basename):
        Structure.__init__(self, basename)
        self.flaps = []

    def add_flap(self, start_station=None, end_station=None,
                 pos=None, type="builtup", angle=30.0,
                 edge_stringer_size=None,
                 mirror=True):

        if start_station == None:
            start_station = self.stations[0]
        if end_station == None:
            end_station = self.stations[len(self.stations)-1]

        flap = Flap( start_station, end_station, pos, angle,
                     edge_stringer_size )
        flap.side = "right"
        self.flaps.append( flap )
        if mirror:
            flap = Flap( -start_station, -end_station, pos, angle,
                         edge_stringer_size )
            flap.side = "left"
            self.flaps.append( flap )

        if flap.edge_stringer_size != None:
            #double_width = flap.edge_stringer_size[0] * 2.0
            half_offset = flap.edge_stringer_size[0] * 0.5
            front_pos = copy.deepcopy(pos)
            front_pos.move(-half_offset)
            topcutout = contour.Cutout( surf="top", orientation="tangent",
                                        cutpos=front_pos,
                                        xsize=flap.edge_stringer_size[0],
                                        ysize=flap.edge_stringer_size[1] )
            stringer = Stringer( topcutout, start_station, end_station, "wing" )
            stringer.side = "right"
            self.stringers.append( stringer )
            if mirror:
                stringer = Stringer( topcutout, -start_station, -end_station, "wing" )
                stringer.side = "left"
                self.stringers.append( stringer )

            botcutout = contour.Cutout( surf="bottom", orientation="tangent",
                                        cutpos=front_pos,
                                        xsize=flap.edge_stringer_size[0],
                                        ysize=flap.edge_stringer_size[1] )
            stringer = Stringer( botcutout, start_station, end_station, "wing" )
            stringer.side = "right"
            self.stringers.append( stringer )
            if mirror:
                stringer = Stringer( botcutout, -start_station, -end_station, "wing" )
                stringer.side = "left"
                self.stringers.append( stringer )

            rear_pos = copy.deepcopy(pos)
            rear_pos.move(half_offset)
            topcutout = contour.Cutout( surf="top", orientation="tangent",
                                        cutpos=rear_pos,
                                        xsize=flap.edge_stringer_size[0],
                                        ysize=flap.edge_stringer_size[1] )
            stringer = Stringer( topcutout, start_station, end_station, "flap" )
            stringer.side = "right"
            self.stringers.append( stringer )
            if mirror:
                stringer = Stringer( topcutout, -start_station, -end_station, "flap" )
                stringer.side = "left"
                self.stringers.append( stringer )

            # the final bottom flap stinger is computed later so we
            # can deal more properly with curved/tapered wings,
            # blended airfoils and get the start/end points of the
            # bottom flap front stringer correct.

    def get_station_rib_type(self, station):
        # for the specified station return position type:
        # inner = inner boundary of a flap
        # outer = outer boundary of a flap
        # shared = outer boundary of one flap and inner boundary of next
        # mid = a middle/supporting rib of a flap
        # none = not part of any flap
        result = "none"
        for flap in self.flaps:
            if self.match_station(flap.start_station, flap.start_station, station):
                if result == "none":
                    result = "inner"
                elif result == "outer":
                    result = "shared"
                else:
                    print "Whoops, something strange in flap ranges"
            elif self.match_station(flap.end_station, flap.end_station, station):
                if result == "none":
                    result = "outer"
                elif result == "inner":
                    result = "shared"
                else:
                    print "Whoops, something strange in flap ranges"
            elif self.match_station(flap.start_station, flap.end_station, station):
                if result == "none":
                    result = "mid"
                else:
                    print "Whoops, something strange in flap ranges"
        return result
        
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
            right_rib.side = "right"
            if percent < 0.001:
                right_rib.nudge = -right_rib.thickness * 0.5
            elif percent > 0.999:
                right_rib.nudge = right_rib.thickness * 0.5
            self.right_ribs.append(right_rib)

            label = 'WL' + str(index+1)
            left_rib = self.make_raw_rib(af, chord, -lat_dist, sweep_dist, \
                                             twist, label)
            left_rib.side = "left"
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
            type = self.get_station_rib_type(rib.pos[0])
            if type == "inner":
                newrib = copy.deepcopy(rib)
                rib.nudge = rib.thickness * 0.75
                newrib.nudge = -rib.thickness * 0.75
                newrib.part = "flap"
                newrib.type = type
                newrib.has_le = False
                new_ribs.append(newrib)
            elif type == "outer":
                newrib = copy.deepcopy(rib)
                rib.nudge = -rib.thickness * 0.75
                newrib.nudge = rib.thickness * 0.75
                newrib.part = "flap"
                newrib.type = type
                newrib.has_le = False
                new_ribs.append(newrib)
            elif type == "shared":
                newrib = copy.deepcopy(rib)
                rib.nudge = rib.thickness * 0.75
                newrib.nudge = -rib.thickness * 0.75
                newrib1 = copy.deepcopy(rib)
                newrib2 = copy.deepcopy(newrib)
                newrib1.part = "flap" 
                newrib2.part = "flap"
                newrib1.type = "outer"
                newrib2.type = "inner"
                newrib1.has_le = False
                newrib2.has_le = False
                rib.has_te = False
                newrib.has_te = False
                new_ribs.append(newrib)
                new_ribs.append(newrib1)
                new_ribs.append(newrib2)
            elif type == "mid":
                #print "match flap at mid station " + str(rib.pos[0])
                newrib = copy.deepcopy(rib)
                newrib.part = "flap"
                newrib.type = type
                newrib.has_le = False
                new_ribs.append(newrib)
                rib.has_te = False

        for rib in new_ribs:
            self.right_ribs.append(rib)
 
        for rib in self.right_ribs:
            rib_pos = rib.pos[0] - rib.nudge
            for flap in self.flaps:
                if self.match_station(flap.start_station, flap.end_station, rib_pos):
                    if rib.part == "flap":
                        pos = rib.trim_front_wedge(flap.pos, flap.angle)
                        if rib.type == "inner":
                            flap.start_bot_str_pos = pos
                            print "flap start bot = " + str(pos)
                        elif rib.type == "outer":
                            flap.end_bot_str_pos = pos
                            print "flap end bot = " + str(pos)
                    else:
                        rib.trim_rear(flap.pos)

        if False:
            new_ribs = []
            for rib in self.left_ribs:
                for flap in self.flaps:
                    if self.match_station(flap.start_station, flap.start_station, rib.pos[0]):
                        #print "start station = " + str(rib.pos[0])
                        newrib = copy.deepcopy(rib)
                        rib.nudge = -rib.thickness * 0.5
                        newrib.nudge = rib.thickness * 1.0
                        flap.start_bot_str_pos = newrib.trim_front_wedge(flap.pos, flap.angle)
                        newrib.part = "flap"
                        newrib.has_le = False
                        new_ribs.append(newrib)
                    elif self.match_station(flap.end_station, flap.end_station, rib.pos[0]):
                        #print "end station = " + str(rib.pos[0])
                        newrib = copy.deepcopy(rib)
                        rib.nudge = rib.thickness * 0.5
                        newrib.nudge = -rib.thickness * 1.0
                        flap.end_bot_str_pos =  newrib.trim_front_wedge(flap.pos, flap.angle)
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
                        #rib.contour.trim(surf="top", discard="rear", cutpos=flap.pos)
                        #rib.contour.trim(surf="bottom", discard="rear", cutpos=flap.pos)
            for rib in new_ribs:
                self.left_ribs.append(rib)
        # end if if False:

        # now place the leading edge bottom stringer for each flap.
        # This is left until now because this can be very dynamic
        # depending on the wing layout and control surface blending.
        for flap in self.flaps:
            if flap.start_bot_str_pos != None and flap.end_bot_str_pos != None \
                    and flap.edge_stringer_size != None:
                xdist = flap.end_station - flap.start_station
                if math.fabs(xdist) > 0.0001:
                    atstation = flap.start_station
                    ydist = flap.end_bot_str_pos - flap.start_bot_str_pos
                    slope = ydist / xdist
                    half_offset = flap.edge_stringer_size[0] * 0.5
                    if flap.side == "left":
                        atstation *= -1.0
                        slope *= -1.0
                    cutpos = contour.Cutpos(xpos=flap.start_bot_str_pos, \
                                                atstation=atstation, \
                                                slope=slope)
                    cutpos.move(half_offset)
                    cutout = contour.Cutout(surf="bottom", \
                                                orientation="tangent", \
                                                cutpos=cutpos, \
                                                xsize=flap.edge_stringer_size[0], \
                                                ysize=flap.edge_stringer_size[1] )
                    print "making bottom stringer: " + str(flap.start_station) + " - " + str(flap.end_station)
                    stringer = Stringer( cutout, flap.start_station, flap.end_station, "flap" )
                    stringer.side = flap.side
                    self.stringers.append( stringer )
            else:
                print "skipped building a flap bottom stringer"
                print str(flap.start_bot_str_pos)
                print str(flap.end_bot_str_pos)
                print str(flap.edge_stringer_size)

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


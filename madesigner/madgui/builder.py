#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
MA builder 

This program loads an xml aircraft and builds it

author: Curtis L. Olson
website: madesigner.flightgear.org
started edited: December 2013
"""

import re
import sys
import os.path

# import numpy here to avoid a glitch in pyinstaller
import numpy

from props import PropertyNode
import props_json

import madlib.ac3d
import madlib.freecad
import madlib.contour
from madlib.wing import Wing

def myfloat(node, name):
    val = node.getString(name)
    if val == '' or val == 'None':
        return 0.0
    else:
        return float(val)

class Builder():

    def __init__(self, filename=None, airfoil_resample=25, circle_points=8,
                 nest_speed="fast"):
        # airfoil_resample: 25 = fast, 100 = mid, 1000 = quality
        # circle_points: 8 = fast, 16 = mid, 32 = quality
        self.airfoil_resample = airfoil_resample
        self.circle_points = circle_points
        self.nest_speed = nest_speed
        self.load(str(filename))

    # return a list of start/end/part triplets for a structure that
    # spans the given start/end stations.  The structure is separated
    # at flap boundaries and marked with part=wing or part=flap
    # accordingly.
    #
    # the idea is that the user is allowed to specify lateral
    # structures along the entire wing and we will split them up as
    # necessary if flaps are defined (the user could also do this the
    # hard way if they really wanted to.)
    def split_for_flaps(self, wing, start, end):
        if start == None:
            start = wing.stations[0]
        if end == None:
            end = wing.stations[len(wing.stations)-1]

        segments = []
        segments.append( (start, end, "wing") )

        for flap in wing.flaps:
            if flap.side == "right":
                #print "flap: " + str( (flap.start_station, flap.end_station) )

                result = []
                for seg in segments:
                    #print "segment: " + str(seg)
                    if seg[2] == 'flap':
                        # copy flap segments verbatim
                        result.append( list(seg) )
                    else:
                        # starting wing portion
                        s1 = seg[0]
                        s2 = seg[1]
                        p1 = s1
                        p2 = flap.start_station
                        if p2 > s2:
                            p2 = s2
                        if p1 < p2:
                            #print "we have starting wing portion"
                            result.append( (p1, p2, "wing") )

                        # flap portion
                        p1 = flap.start_station
                        p2 = flap.end_station
                        if p1 < s1:
                            p1 = s1
                        if p2 > s2:
                            p2 = s2
                        if p1 < p2:
                            result.append( (p1, p2, "flap") )

                        # ending wing portion
                        p1 = flap.end_station
                        p2 = s2
                        if p1 < s1:
                            p1 = s1
                        if p1 < p2:
                            #print "we have ending wing portion"
                            result.append( (p1, p2, "wing") )
                #print "after flap, result = " + str(result)
                segments = list(result)

        #print str(segments)
        return segments

        
    def parse_overview(self, node):
        self.units = node.getString('units')
        self.sheet_w = myfloat(node, 'sheet_width')
        self.sheet_h = myfloat(node, 'sheet_height')
        self.plans_w = myfloat(node, 'plans_width')
        self.plans_h = myfloat(node, 'plans_height')

    def parse_leading_edge(self, wing, node):
        size = myfloat(node, 'size')
        tokens = node.getString('start_station').split()
        print 'le:', len(tokens), tokens
        if len(tokens) == 2 and tokens[1] != 'Inner':
            start = float(tokens[1])
        else:
            start = None
        tokens = node.getString('end_station').split()
        if len(tokens) == 2 and tokens[1] != 'Outer':
            end = float(tokens[1])
        else:
            end = None
        wing.add_leading_edge(size=size, start_station=start, end_station=end, part="wing")

    def parse_trailing_edge(self, wing, node):
        width = myfloat(node, 'width')
        height = myfloat(node, 'height')
        shape = node.getString('shape')
        tokens = node.getString('start_station').split()
        if len(tokens) == 2 and tokens[1] != 'Inner':
            start = float(tokens[1])
        else:
            start = None
        tokens = node.getString('end_station').split()
        if len(tokens) == 2 and tokens[1] != 'Outer':
            end = float(tokens[1])
        else:
            end = None
        parts = self.split_for_flaps(wing, start, end)
        for p in parts: 
            wing.add_trailing_edge(width=width, height=height, shape=shape, start_station=p[0], end_station=p[1], part=p[2])

    def parse_stringer(self, wing, node):
        width = myfloat(node, 'width')
        height = myfloat(node, 'height')
        position_ref = node.getString('position_ref')
        position_val = myfloat(node, 'position')
        percent = None
        front = None
        rear = None
        xpos = None
        if position_ref == "Chord %":
            percent = position_val
        elif position_ref == "Rel Front":
            front = position_val
        elif position_ref == "Rel Rear":
            rear = position_val
        elif position_ref == "Abs Pos":
            xpos = position_val
        surface = node.getString('surface').lower()
        tokens = node.getString('start_station').split()
        if len(tokens) == 2 and tokens[1] != 'Inner':
            start = float(tokens[1])
        else:
            start = None
        tokens = node.getString('end_station').split()
        if len(tokens) == 2 and tokens[1] != 'Outer':
            end = float(tokens[1])
        else:
            end = None
        wing.add_stringer(surf=surface, orientation="tangent", percent=percent, front=front, rear=rear, xpos=xpos, xsize=width, ysize=height, start_station=start, end_station=end, part="wing")

    def parse_spar(self, wing, node):
        width = myfloat(node, 'width')
        height = myfloat(node, 'height')
        position_ref = node.getString('position_ref')
        position_val = myfloat(node, 'position')
        percent = None
        front = None
        rear = None
        xpos = None
        if position_ref == "Chord %":
            percent = position_val
        elif position_ref == "Rel Front":
            front = position_val
        elif position_ref == "Rel Rear":
            rear = position_val
        elif position_ref == "Abs Pos":
            xpos = position_val
        surface = node.getString('surface').lower()
        tokens = node.getString('start_station').split()
        if len(tokens) == 2 and tokens[1] != 'Inner':
            start = float(tokens[1])
        else:
            start = None
        tokens = node.getString('end_station').split()
        if len(tokens) == 2 and tokens[1] != 'Outer':
            end = float(tokens[1])
        else:
            end = None
        wing.add_spar(surf=surface, orientation="vertical", percent=percent, front=front, rear=rear, xpos=xpos, xsize=width, ysize=height, start_station=start, end_station=end, part="wing")

    def parse_sheet(self, wing, node):
        depth = myfloat(node, 'depth')
        xstart = myfloat(node, 'xstart')
        xmode = node.getString('xmode')
        dist = myfloat(node, 'xend')
        xend = None
        xdist = None
        if xmode == "Sheet Width":
            xdist = dist
        elif xmode == "End Position":
            xend = dist
        surface = node.getString('surface').lower()
        tokens = node.getString('start_station').split()
        if len(tokens) == 2 and tokens[1] != 'Inner':
            start = float(tokens[1])
        else:
            start = None
        tokens = node.getString('end_station').split()
        if len(tokens) == 2 and tokens[1] != 'Outer':
            end = float(tokens[1])
        else:
            end = None
        #print str(surface) + " " + str(xstart) + " " + str(xend) + " " + str(xdist) + " " + str(depth) + " " + str(start) + " " + str(end)
        wing.add_sheeting(surf=surface, xstart=xstart, xend=xend, xdist=xdist, ysize=depth, start_station=start, end_station=end, part="wing")

    def parse_simple_hole(self, wing, node):
        style = node.getString('style')
        size = myfloat(node, 'size')
        position_ref = node.getString('position_ref')
        position_val = myfloat(node, 'position')
        percent = None
        front = None
        rear = None
        xpos = None
        if position_ref == "Chord %":
            percent = position_val
        elif position_ref == "Rel Front":
            front = position_val
        elif position_ref == "Rel Rear":
            rear = position_val
        elif position_ref == "Abs Pos":
            xpos = position_val
        tokens = node.getString('start_station').split()
        if len(tokens) == 2 and tokens[1] != 'Inner':
            start = float(tokens[1])
        else:
            start = None
        tokens = node.getString('end_station').split()
        if len(tokens) == 2 and tokens[1] != 'Outer':
            end = float(tokens[1])
        else:
            end = None
        pos=madlib.contour.Cutpos(percent=percent, front=front, rear=rear, xpos=xpos)
        wing.add_simple_hole(style=style, size=size, pos1=pos, start_station=start, end_station=end, part="wing")

    def parse_shaped_hole(self, wing, node):
        width = myfloat(node, 'material_width')
        radius = myfloat(node, 'corner_radius')

        position1_ref = node.getString('position1_ref')
        position1_val = myfloat(node, 'position1')
        percent = None
        front = None
        rear = None
        xpos = None
        if position1_ref == "Chord %":
            percent = position1_val
        elif position1_ref == "Rel Front":
            front = position1_val
        elif position1_ref == "Rel Rear":
            rear = position1_val
        elif position1_ref == "Abs Pos":
            xpos = position1_val
        pos1=madlib.contour.Cutpos(percent=percent, front=front, rear=rear, xpos=xpos)

        position2_ref = node.getString('position2_ref')
        position2_val = myfloat(node, 'position2')
        percent = None
        front = None
        rear = None
        xpos = None
        if position2_ref == "Chord %":
            percent = position2_val
        elif position2_ref == "Rel Front":
            front = position2_val
        elif position2_ref == "Rel Rear":
            rear = position2_val
        elif position2_ref == "Abs Pos":
            xpos = position2_val
        pos2=madlib.contour.Cutpos(percent=percent, front=front, rear=rear, xpos=xpos)

        tokens = node.getString('start_station').split()
        if len(tokens) == 2 and tokens[1] != 'Inner':
            start = float(tokens[1])
        else:
            start = None
        tokens = node.getString('end_station').split()
        if len(tokens) == 2 and tokens[1] != 'Outer':
            end = float(tokens[1])
        else:
            end = None

        wing.add_shaped_hole(pos1=pos1, pos2=pos2, material_width=width, radius=radius, start_station=start, end_station=end, part="wing")

    def parse_build_tab(self, wing, node):
        width = myfloat(node, 'width')
        ypad = myfloat(node, 'ypad')
        position_ref = node.getString('position_ref')
        position_val = myfloat(node, 'position')
        percent = None
        front = None
        rear = None
        xpos = None
        if position_ref == "Chord %":
            percent = position_val
        elif position_ref == "Rel Front":
            front = position_val
        elif position_ref == "Rel Rear":
            rear = position_val
        elif position_ref == "Abs Pos":
            xpos = position_val
        surface = node.getString('surface').lower()
        tokens = node.getString('start_station').split()
        if len(tokens) == 2 and tokens[1] != 'Inner':
            start = float(tokens[1])
        else:
            start = None
        tokens = node.getString('end_station').split()
        if len(tokens) == 2 and tokens[1] != 'Outer':
            end = float(tokens[1])
        else:
            end = None
        wing.add_build_tab(surf=surface, percent=percent, front=front, rear=rear, xpos=xpos, xsize=width, ypad=ypad, start_station=start, end_station=end, part="wing")

    def parse_flap(self, wing, node):
        width = myfloat(node, 'width')
        height = myfloat(node, 'height')
        position_ref = node.getString('position_ref')
        position_val = myfloat(node, 'position')
        percent = None
        front = None
        rear = None
        xpos = None
        if position_ref == "Chord %":
            percent = position_val
        elif position_ref == "Rel Front":
            front = position_val
        elif position_ref == "Rel Rear":
            rear = position_val
        elif position_ref == "Abs Pos":
            xpos = position_val
        start_text = node.getString('start_station')
        if start_text == "":
            print "Invalid start station for flap"
            return
        junk, start_str = start_text.split()
        if start_str == "Inner" or start_str == "":
            start = None
        else:
            start = float(start_str)
        end_text = node.getString('end_station')
        if end_text == "":
            print "Invalid end station for flap"
            return
        junk, end_str = end_text.split()
        if end_str == "Outer" or end_str == "":
            end = None
        else:
            end = float(end_str)
        atstation = myfloat(node, 'at_station')
        slope = myfloat(node, 'slope')
        angle = myfloat(node, 'angle')
        pos = madlib.contour.Cutpos(percent=percent, front=front, rear=rear, xpos=xpos, atstation=atstation, slope=slope)
        size = ( width, height )
        wing.add_flap( start_station=start, end_station=end, pos=pos, type="builtup", angle=angle, edge_stringer_size=size)

    def make_curve(self, text):
        #print text
        curve = []
        pairs = re.split( "\)\s*\(", text )
        for p in pairs:
            p = re.sub( "\s*\(\s*", "", p)
            p = re.sub( "\s*\)\s*", "", p)
            #print " p=" + p
            #print " search=" + str(re.search("\,", p))
            if re.search("\,", p):
                x, y = re.split( "\s*,\s*", p )
                curve.append( (float(x), float(y)) )
        #print str(curve)
        return curve                         
        
    def parse_wing(self, node):
        wing = Wing(self.fileroot)
        wing.units = self.units
        wing.airfoil_resample = self.airfoil_resample
        wing.circle_points=self.circle_points
        wing.name = node.getString('name')
        airfoil_root = node.getString('airfoil_root')
        airfoil_tip = node.getString('airfoil_tip')
        if airfoil_tip == "":
            airfoil_tip = None
        wing.load_airfoils( airfoil_root, airfoil_tip )
        wing.span = myfloat(node, 'span')
        station_list = map( float, str(node.getString('stations')).split())
        wing.set_stations( station_list )
        wing.twist = myfloat(node, 'twist')
        sweep_curve = self.make_curve( node.getString('sweep_curve') )
        if ( len(sweep_curve) >= 2 ):
            wing.set_sweep_curve( sweep_curve )
        else:
            wing.set_sweep_angle( myfloat(node, 'sweep') )
        chord_curve = self.make_curve( node.getString('chord_curve') )
        if ( len(chord_curve) >= 2 ):
            wing.set_taper_curve( chord_curve )
        else:
            chord_root = myfloat(node, 'chord_root')
            chord_tip = myfloat(node, 'chord_tip')
            wing.set_chord( chord_root, chord_tip )
        wing.dihedral = myfloat(node, 'dihedral')
        wing.link_name = node.getString('wing_link')

        # parse flaps first so we can use this info to partition the
        # trailing edge and possibly other structures too
        for i in range(node.getLen('flap')):
            self.parse_flap(wing, node.getChild('flap[%d]' % i))
        for i in range(node.getLen('leading_edge')):
            self.parse_leading_edge(wing, node.getChild('leading_edge[%d]' % i))
        for i in range(node.getLen('trailing_edge')):
            self.parse_trailing_edge(wing, node.getChild('trailing_edge[%d]' % i))
        for i in range(node.getLen('spar')):
            self.parse_spar(wing, node.getChild('spar[%d]' % i))
        for i in range(node.getLen('stringer')):
            self.parse_stringer(wing, node.getChild('stringer[%d]' % i))
        for i in range(node.getLen('sheet')):
            self.parse_sheet(wing, node.getChild('sheet[%d]' % i))
        for i in range(node.getLen('simple_hole')):
            self.parse_simple_hole(wing, node.getChild('simple_hole[%d]' % i))
        for i in range(node.getLen('shaped_hole')):
            self.parse_shaped_hole(wing, node.getChild('shaped_hole[%d]' % i))
        for i in range(node.getLen('build_tab')):
            self.parse_build_tab(wing, node.getChild('build_tab[%d]' % i))

        wing.build()
        wing.layout_parts_sheets( self.sheet_w, self.sheet_h, units=self.units,
                                  speed=self.nest_speed)
        #wing.layout_parts_templates( 8.5, 11 )
        wing.layout_plans( self.plans_w, self.plans_h, units=self.units )

        return wing

    def find_wing_by_name(self, name):
        i = 0
        for wing in self.wings:
            if wing.name == name:
                return i
            i += 1
        # no match
        return -1

    def load(self, filename):
        if not os.path.exists(filename):
            print "Error, design not found: " + filename
            return

        design = PropertyNode()
        if not props_json.load(filename, design):
            print filename + ": xml parse error:\n" + str(sys.exc_info()[1])
            return

        self.fileroot, ext = os.path.splitext(filename)
        self.basename = os.path.basename(filename)
        self.baseroot, ext = os.path.splitext(self.basename)

        node = design.getChild('overview', True)
        self.parse_overview(node)

        self.wings = []
        for i in range(design.getLen('wing')):
            wing_node = design.getChild('wing[%d]' % i)
            wing = self.parse_wing(wing_node)
            self.wings.append(wing)

        # generate AC3D model
        # if len(self.wings):
        #     ac = madlib.ac3d.AC3D( self.fileroot )
        #     ac.gen_headers( "airframe", 2 )
        #     for wing in self.wings:
        #         tip = [ 0.0, 0.0, 0.0 ]
        #         if wing.link_name != None and wing.link_name != "none":
        #             i = self.find_wing_by_name( wing.link_name )
        #             if i >= 0:
        #                 tip = self.wings[i].get_tip_pos()
        #         wing.build_ac3d( ac, xoffset=tip[1], yoffset=tip[2] )
        #     ac.close()
            
        # generate FreeCAD model
        doc = madlib.freecad.GenFreeCAD()
        doc.start_model("my document")
        if len(self.wings):
            for wing in self.wings:
                tip = [ 0.0, 0.0, 0.0 ]
                if wing.link_name != None and wing.link_name != "none":
                    i = self.find_wing_by_name( wing.link_name )
                    if i >= 0:
                        tip = self.wings[i].get_tip_pos()
                wing.build_freecad( doc, xoffset=tip[1], yoffset=tip[2] )
        doc.view_stl()
        doc.save_model("name");

def usage():
    print "Usage: " + sys.argv[0] + " design.mad"

def main():
    initfile = ""
    if len(sys.argv) != 2:
        usage()
        return
    else:
        initfile = sys.argv[1]
    build = Builder(initfile)

if __name__ == '__main__':
    main()

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
#import xml.etree.ElementTree as ET
import lxml.etree as ET

# import numpy here to avoid a glitch in pyinstaller
import numpy

import lib.ac3d
import lib.contour
from lib.wing import Wing


def get_value(xml, name):
    e = xml.find(name)
    if e != None and e.text != None:
        return e.text
    else:
        return ""

def myfloat(input):
    if input == "":
        return 0.0
    else:
        return float(input)

class Builder():

    def __init__(self, filename=None, airfoil_resample=25, circle_points=8):
        # airfoil_resample: 25 = fast, 100 = mid, 1000 = quality
        # circle_points: 8 = fast, 16 = mid, 32 = quality
        self.airfoil_resample = airfoil_resample
        self.circle_points = circle_points

        root = ET.Element('design')
        self.xml = ET.ElementTree(root)

        self.load(filename)

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
        self.units = get_value(node, 'units')
        self.sheet_w = myfloat(get_value(node, 'sheet-width'))
        self.sheet_h = myfloat(get_value(node, 'sheet-height'))
        self.plans_w = myfloat(get_value(node, 'plans-width'))
        self.plans_h = myfloat(get_value(node, 'plans-height'))

    def parse_leading_edge(self, wing, node):
        size = float(get_value(node, 'size'))
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        wing.add_leading_edge(size=size, start_station=start, end_station=end, part="wing")

    def parse_trailing_edge(self, wing, node):
        width = float(get_value(node, 'width'))
        height = float(get_value(node, 'height'))
        shape = get_value(node, 'shape')
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        parts = self.split_for_flaps(wing, start, end)
        for p in parts: 
            wing.add_trailing_edge(width=width, height=height, shape=shape, start_station=p[0], end_station=p[1], part=p[2])

    def parse_stringer(self, wing, node):
        width = float(get_value(node, 'width'))
        height = float(get_value(node, 'height'))
        position_ref = get_value(node, 'position-ref')
        position_val = float(get_value(node, 'position'))
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
        surface = get_value(node, 'surface').lower()
        #orientation = get_value(node, 'orientation').lower()
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        wing.add_stringer(surf=surface, orientation="tangent", percent=percent, front=front, rear=rear, xpos=xpos, xsize=width, ysize=height, start_station=start, end_station=end, part="wing")

    def parse_spar(self, wing, node):
        width = float(get_value(node, 'width'))
        height = float(get_value(node, 'height'))
        position_ref = get_value(node, 'position-ref')
        position_val = float(get_value(node, 'position'))
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
        surface = get_value(node, 'surface').lower()
        #orientation = get_value(node, 'orientation').lower()
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        wing.add_spar(surf=surface, orientation="vertical", percent=percent, front=front, rear=rear, xpos=xpos, xsize=width, ysize=height, start_station=start, end_station=end, part="wing")

    def parse_sheet(self, wing, node):
        depth = float(get_value(node, 'depth'))
        xstart = float(get_value(node, 'xstart'))
        xmode = get_value(node, 'xmode')
        dist = float(get_value(node, 'xend'))
        xend = None
        xdist = None
        if xmode == "Sheet Width":
            xdist = dist
        elif xmode == "End Position":
            xend = dist
        surface = get_value(node, 'surface').lower()
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        #print str(surface) + " " + str(xstart) + " " + str(xend) + " " + str(xdist) + " " + str(depth) + " " + str(start) + " " + str(end)
        wing.add_sheeting(surf=surface, xstart=xstart, xend=xend, xdist=xdist, ysize=depth, start_station=start, end_station=end, part="wing")

    def parse_simple_hole(self, wing, node):
        radius = float(get_value(node, 'radius'))
        position_ref = get_value(node, 'position-ref')
        position_val = float(get_value(node, 'position'))
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
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)

        pos=lib.contour.Cutpos(percent=percent, front=front, rear=rear, xpos=xpos)
        wing.add_simple_hole(radius=radius, pos1=pos, start_station=start, end_station=end, part="wing")

    def parse_shaped_hole(self, wing, node):
        width = float(get_value(node, 'material-width'))
        radius = float(get_value(node, 'corner-radius'))

        position1_ref = get_value(node, 'position1-ref')
        position1_val = float(get_value(node, 'position1'))
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
        pos1=lib.contour.Cutpos(percent=percent, front=front, rear=rear, xpos=xpos)

        position2_ref = get_value(node, 'position2-ref')
        position2_val = float(get_value(node, 'position2'))
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
        pos2=lib.contour.Cutpos(percent=percent, front=front, rear=rear, xpos=xpos)

        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)

        wing.add_shaped_hole(pos1=pos1, pos2=pos2, material_width=width, radius=radius, start_station=start, end_station=end, part="wing")

    def parse_build_tab(self, wing, node):
        width = myfloat(get_value(node, 'width'))
        ypad = myfloat(get_value(node, 'ypad'))
        position_ref = get_value(node, 'position-ref')
        position_val = float(get_value(node, 'position'))
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
        surface = get_value(node, 'surface').lower()
        junk, startstr = get_value(node, 'start-station').split()
        junk, endstr = get_value(node, 'end-station').split()
        if startstr == "Inner" or startstr == "":
            start = None
        else:
            start = float(startstr)
        if endstr == "Outer" or endstr == "":
            end = None
        else:
            end = float(endstr)
        wing.add_build_tab(surf=surface, percent=percent, front=front, rear=rear, xpos=xpos, xsize=width, ypad=ypad, start_station=start, end_station=end, part="wing")

    def parse_flap(self, wing, node):
        width = float(get_value(node, 'width'))
        height = float(get_value(node, 'height'))
        position_ref = get_value(node, 'position-ref')
        position_val = float(get_value(node, 'position'))
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
        start_text = get_value(node, 'start-station')
        if start_text == "":
            print "Invalid start station for flap"
            return
        junk, start_str = start_text.split()
        if start_str == "Inner" or start_str == "":
            start = None
        else:
            start = myfloat(start_str)
        end_text = get_value(node, 'end-station')
        if end_text == "":
            print "Invalid end station for flap"
            return
        junk, end_str = end_text.split()
        if end_str == "Outer" or end_str == "":
            end = None
        else:
            end = myfloat(end_str)
        atstation = myfloat(get_value(node, 'at-station'))
        slope = myfloat(get_value(node, 'slope'))
        angle = myfloat(get_value(node, 'angle'))
        pos = lib.contour.Cutpos(percent=percent, front=front, rear=rear, xpos=xpos, atstation=atstation, slope=slope)
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
        wing.name = get_value(node, 'name')
        airfoil_root = get_value(node, 'airfoil-root')
        airfoil_tip = get_value(node, 'airfoil-tip')
        if airfoil_tip == "":
            airfoil_tip = None
        wing.load_airfoils( airfoil_root, airfoil_tip )
        wing.span = float(get_value(node, 'span'))
        station_list = map( float, str(get_value(node, 'stations')).split())
        wing.set_stations( station_list )
        wing.twist = myfloat(get_value(node, 'twist'))
        sweep_curve = self.make_curve( get_value(node, 'sweep-curve') )
        if ( len(sweep_curve) >= 2 ):
            wing.set_sweep_curve( sweep_curve )
        else:
            wing.set_sweep_angle( myfloat(get_value(node, 'sweep')) )
        chord_curve = self.make_curve( get_value(node, 'chord-curve') )
        if ( len(chord_curve) >= 2 ):
            wing.set_taper_curve( chord_curve )
        else:
            chord_root = myfloat(get_value(node, 'chord-root'))
            chord_tip = myfloat(get_value(node, 'chord-tip'))
            wing.set_chord( chord_root, chord_tip )
        wing.dihedral = myfloat(get_value(node, 'dihedral'))
        wing.link_name = get_value(node, 'wing-link')

        # parse flaps first so we can use this info to partition the
        # trailing edge and possibly other structures too
        for flap_node in node.findall('flap'):
            self.parse_flap(wing, flap_node)

        for le_node in node.findall('leading-edge'):
            self.parse_leading_edge(wing, le_node)
        for te_node in node.findall('trailing-edge'):
            self.parse_trailing_edge(wing, te_node)
        for spar_node in node.findall('spar'):
            self.parse_spar(wing, spar_node)
        for stringer_node in node.findall('stringer'):
            self.parse_stringer(wing, stringer_node)
        for sheet_node in node.findall('sheet'):
            self.parse_sheet(wing, sheet_node)
        for hole_node in node.findall('simple-hole'):
            self.parse_simple_hole(wing, hole_node)
        for hole_node in node.findall('shaped-hole'):
            self.parse_shaped_hole(wing, hole_node)
        for tab_node in node.findall('build-tab'):
            self.parse_build_tab(wing, tab_node)

        wing.build()
        wing.layout_parts_sheets( self.sheet_w, self.sheet_h, units=self.units )
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

        try:
            self.xml = ET.parse(filename)
        except:
            print filename + ": xml parse error:\n" + str(sys.exc_info()[1])
            return

        self.fileroot, ext = os.path.splitext(filename)
        self.basename = os.path.basename(filename)
        self.baseroot, ext = os.path.splitext(self.basename)

        root = self.xml.getroot()

        node = root.find('overview')
        self.parse_overview(node)

        self.wings = []
        for wing_node in root.findall('wing'):
            wing = self.parse_wing(wing_node)
            self.wings.append(wing)

        if len(self.wings):
            ac = lib.ac3d.AC3D( self.fileroot )
            ac.gen_headers( "airframe", 2 )
            for wing in self.wings:
                tip = [ 0.0, 0.0, 0.0 ]
                if wing.link_name != None and wing.link_name != "none":
                    i = self.find_wing_by_name( wing.link_name )
                    if i >= 0:
                        tip = self.wings[i].get_tip_pos()
                wing.build_ac3d( ac, xoffset=tip[1], yoffset=tip[2] )
            ac.close()


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

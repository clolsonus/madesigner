#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import sys
import os.path
import fileinput
import math
import string
import re
import Polygon

from contour import Contour
import spline

datapath = "../data"

class Airfoil(Contour):

    def __init__(self, name = "", samples = 0, use_spline = False):
        Contour.__init__(self)
        # locate airfoils data path relative to top level script
        datapath = os.path.split(os.path.abspath(sys.argv[0]))[0] + "/data"
        self.datapath = datapath
        self.name = ""
        self.description = ""
        # parametric representation of the airfoil dist along surface
        # vs. x and vs. y
        self.parax = []
        self.paray = []
        self.nosedist = 0.0
        if ( name != "" ):
            self.load(name, samples, use_spline)

    def load(self, base, samples = 0, use_spline = False):
        self.name = base
        path = self.datapath + "/airfoils/" + base + ".dat"
        top = True
        dist = 0.0
        dlast = 0.0
        xlast = None
        ylast = None
        f = fileinput.input(path)
        for line in f:
            #print line
            line = line.strip()
            if f.isfirstline():
                self.description = string.join(line.split())
                continue
            xa, ya = line.split()
            if ya == "......" or ya == ".......":
                # ya = "0.0"
                continue
            x = float(xa)
            if x >= 100.0:
                continue
            y = 0.0
            m = re.search('\(([\d\.\-]+)\)', ya)
            if m != None:
                y = float(m.group(1))
                #print str(y)
            else:
                y = float(ya)
            # print str(x) + " " + str(y)
            if x != xlast:
                dist += self.dist_2d( (xlast, ylast), (x, y) )
                self.parax.append( (dist, x) )
                self.paray.append( (dist, y) )
                if top and xlast != None and x - xlast > 0.0:
                    # mark the exact airfoil nose in parameterized
                    # surface distance space
                    self.nosedist = dlast
                    top = False
                    self.bottom.append( (xlast, ylast) )
                if top:
                    self.top.append( (x, y) )
                else:
                    self.bottom.append( (x, y) )
                xlast = x
                ylast = y
                dlast = dist
        self.top.reverse()
        #print str(self.top)
        #print str(self.bottom)
        #self.display()
        #print "PARAX"
        #for pt in self.parax:
        #    print str(pt[0]) + " " + str(pt[1])
        #print "PARAY"
        #for pt in self.paray:
        #    print str(pt[0]) + " " + str(pt[1])
        if samples > 0:
            self.resample( samples, use_spline )
            #print "RESAMPLE"
            #print str(self.top)
            #print str(self.bottom)
            #self.display()

    def resample(self, xdivs, use_spline):
        self.top = []
        self.bottom = []
        n = len(self.parax)
        totaldist = self.parax[n-1][0]
        # print "total surface dist = " + str(totaldist)

        # extract the top surface
        step = self.nosedist / xdivs
        parax_y2 = spline.derivative2( self.parax )
        paray_y2 = spline.derivative2( self.paray )
        for i in range(0, xdivs+1):
            d = i * step
            if use_spline:
                index = spline.binsearch(self.parax, d)
                x = spline.spline(self.parax, parax_y2, index, d)
                y = spline.spline(self.paray, paray_y2, index, d)
            else:
                x = self.simple_interp(self.parax, d )
                y = self.simple_interp(self.paray, d )
            if x >= 0.0:
                #print str(x) + " " + str(y)
                self.top.append( (x, y) )
        self.top.reverse()

        # extract the bottom surface
        step = (totaldist - self.nosedist) / xdivs
        for i in range(0, xdivs+1):
            d = i * step + self.nosedist
            if use_spline:
                index = spline.binsearch(self.parax, d)
                x = spline.spline(self.parax, parax_y2, index, d)
                y = spline.spline(self.paray, paray_y2, index, d)
            else:
                x = self.simple_interp(self.parax, d )
                y = self.simple_interp(self.paray, d )
            if x < 0.0:
                x = 0.0
            self.bottom.append( (x, y) )

    def walk_curve_from_front(self, curve, xstart, target_dist):
        #print "walk from " + str(xstart) + " dist of " + str(target_dist)
        n = len(curve)
        dist = 0
        cur = ( xstart, self.simple_interp(curve, xstart) )
        next_index = spline.binsearch(curve, xstart) + 1
        if next_index < n:
            dist_to_next = self.dist_2d(cur, curve[next_index])
        else:
            # ran out of points
            return cur[0]
        #print "idx = " + str(next_index) + " dist_to_next = " + str(dist_to_next)
        while dist + dist_to_next < target_dist:
            dist += dist_to_next
            cur = curve[next_index]
            next_index += 1
            if next_index < n:
                dist_to_next = self.dist_2d(cur, curve[next_index])
            else:
                # ran out of points
                return cur[0]
        rem = target_dist - dist
        pct = rem / dist_to_next
        dx = curve[next_index][0] - cur[0]

        return cur[0] + dx * pct

    def walk_curve_from_back(self, curve, xend, target_dist):
        print "walk from " + str(xend) + " dist of " + str(target_dist)
        n = len(curve)
        print "curve is " + str(n) + " points"
        dist = 0
        cur = ( xend, self.simple_interp(curve, xend) )
        prior_index = spline.binsearch(curve, xend)
        print "prior_index = " + str(prior_index)
        if prior_index >= 0:
            dist_to_prior = self.dist_2d(cur, curve[prior_index])
        else:
            # ran out of points
            return cur[0]
        print "idx = " + str(prior_index) + " dist_to_prior = " + str(dist_to_prior)
        while dist + dist_to_prior < target_dist:
            dist += dist_to_prior
            cur = curve[prior_index]
            prior_index -= 1
            if prior_index >= 0:
                dist_to_prior = self.dist_2d(cur, curve[prior_index])
            else:
                # ran out of points
                return cur[0]
        rem = target_dist - dist
        pct = rem / dist_to_prior
        dx = cur[0] - curve[prior_index][0]

        return cur[0] - dx * pct

    def cutout_leading_edge_diamond(self, size, pos=None, nudge=0.0):
        # make the Polygon representation of this part if needed
        if self.poly == None:
            self.make_poly()

        target_diag = math.sqrt(2*size*size)
        # walk backwards equal amounts along both top and bottom curves until
        # find the first points that are diag apart.
        cur_diag = 0
        step = 0.001
        dist = step
        n = len(self.top)
        xstart = self.top[0][0]
        chord = self.top[n-1][0] - xstart
        while cur_diag < target_diag and dist < chord:
            xtop = self.walk_curve_from_front(self.top, xstart, dist)
            ytop = self.simple_interp(self.top, xtop)
            xbottom = self.walk_curve_from_front(self.bottom, xstart, dist)
            ybottom = self.simple_interp(self.bottom, xbottom)
            cur_diag = self.dist_2d( (xtop, ytop), (xbottom, ybottom) )
            dist += step
        if dist >= chord:
            print "unable to fit leading edge, stock diagonal longer than rib height?"
            return []
        #print (xtop, ytop)
        #print (xbottom, ybottom)
        #print (cur_diag, target_diag)
        dx = xtop - xbottom
        dy = ytop - ybottom
        angle = math.degrees(math.atan2(dy,dx))
        #print angle
        a45 = angle + 45
        #print a45
        r0 = self.rotate_point( (-size, 0), a45 )
        #print r0
        corner = ( xtop + r0[0], ytop + r0[1] )
        #print self.dist_2d( (xtop, ytop), corner )
        #print self.dist_2d( corner, (xbottom, ybottom) )

        # make mask shape
        p1 = (xbottom, ybottom)
        p2 = corner
        p3 = (xtop, ytop)
        p4 = ( xtop-size*1.5, ytop )
        p5 = ( xbottom-size*1.5, ybottom )
        mask = Polygon.Polygon( (p1, p2, p3, p4, p5) )
        self.poly = self.poly - mask

        # also make the true shape while we are here (reusing the
        # bottom of the cut mask)
        p1 = (xbottom, ybottom)
        p2 = corner
        p3 = (xtop, ytop)
        p4 = self.top[0]
        v1 = ( p1[0]+pos[1], pos[0]-nudge, p1[1] )
        v2 = ( p2[0]+pos[1], pos[0]-nudge, p2[1] )
        v3 = ( p3[0]+pos[1], pos[0]-nudge, p3[1] )
        v4 = ( p4[0]+pos[1], pos[0]-nudge, p4[1] )
        shape = (v1, v2, v3, v4)
        return shape


    def cutout_trailing_edge(self, width=0.0, height=0.0, shape="",
                             force_fit=False, pos=None, nudge=0.0):
        if shape == "Flat Triangle" or shape == "Symmetrical":
            result = self.cutout_trailing_edge_triangle(width, height, shape,
                                                        force_fit, pos, nudge)
        elif shape == "Bottom Sheet":
            result = self.cutout_trailing_edge_sheet(width, height, shape,
                                                     force_fit, pos, nudge)
        return result
            
    # Important note: If calling the trailing edge cutout function
    # with force_fit, then please notice that this routine modifies
    # the basic airfoil shape and rebuilds the self.poly object from
    # scratch.  Thus, it should be called before any other cutouts are
    # made to the part or those prior cutout will be lost.  More
    # specifically it will do the following.  (1) find the best fit /
    # alignment of the specified trailing edge stock (matches the
    # exact trailing edge point and then does a best fit rotation from
    # there.)  (2) compute the vertical error at the attach point
    # between the original airfoil and the trailing edge stock
    # (factoring in any alignment rotation or angled intesection that
    # might have been computed at the best fit stage.)  (3) shave a
    # subtle wedge off the back 2/3 of the airfoil to make an exact
    # fit (or add material if the airfoil is too thin rather than too
    # thick.  This would be analogous to a builder carefully sanding
    # the back 2/3 of the rib to match the trailing edge stock and
    # taking just the right amount off both the top and bottom evenly
    # to minimize changes to the original airfoil shape.
    #
    # Sorry for the long complicated explanation!
    #
    def cutout_trailing_edge_triangle(self, width=0.0, height=0.0, shape="",
                                      force_fit=True, pos=None, nudge=0.0):
        h2 = height*0.5
        if shape == "Flat Triangle":
            bottom_dist = width
            mid_dist = math.sqrt(width*width + h2*h2)
            top_dist = math.sqrt(width*width + height*height)
        elif shape == "Symmetrical":
            bottom_dist = math.sqrt(width*width + h2*h2)
            mid_dist = width
            top_dist = bottom_dist
        elif shape == "Bottom Sheet":
            bottom_dist = width
            top_dist = width
            mid_dist = width
        else:
            print "Unknown trailing edge shape. Must be Flat Triangle, Symmetrical, or Bottom Sheet."
            return

        # make the Polygon representation of this part if needed
        if self.poly == None:
            self.make_poly()

        tn = len(self.top)
        bn = len(self.bottom)
        xnose = self.top[0][0]
        xtail = self.top[tn-1][0]
        yttail = self.top[tn-1][1]
        ybtail = self.bottom[bn-1][1]
        ytail = (yttail + ybtail) * 0.5
        chord = xtail - xnose
        if top_dist > chord or bottom_dist > chord:
            # unable
            return

        step = 0.001
        xpos = xtail - step
        cur_mid = step
        # walk forward specified distances along top and bottom curves
        # (starting at the back)
        ytop = 0.0
        ybottom = 0.0
        while cur_mid <= mid_dist and xpos >= xnose:
            ytop = self.simple_interp(self.top, xpos)
            ybottom = self.simple_interp(self.bottom, xpos)
            ymid = (ytop + ybottom) * 0.5
            cur_mid = self.dist_2d( (xtail, ytail), (xpos, ymid) )
            xpos -= step

        dx = xpos - xtail
        dy = ymid - ytail
        #print (dx, dy)
        angle = math.atan2(dy, -dx)
        #print "angle = " + str(math.degrees(angle))

        #print "Trailing edge: stock height = " + str(height)
        #print "Rotated stock end height = " + str(height*math.cos(angle))
        #print "Rib height at cut pt = " + str(ytop - ybottom)

        if force_fit:
            # cheat the vertical scale of the rib to match the stock
            # size (linearly distorting 1.0 scale at nose, to whatever
            # scale required at te point.  (1/2 the difference between
            # the vertical component of the te stock and the actual
            # airfoil vertical height at that point.)
            ycheat = 0.5 * (height*math.cos(angle) - (ytop - ybottom))
            #print "ycheat = " + str(ycheat) + " @ " + str(xpos)
            newtop = []
            newbottom = []
            newpoly = Polygon.Polygon()
            for i, pt in enumerate(self.top):
                xcur = self.top[i][0]
                ycur = self.top[i][1]
                if i < len(self.top)-1:
                    xnext = self.top[i+1][0]
                else:
                    xnext = None
                if xcur < 0.0:
                    offset = 0.0
                elif xcur <= xpos:
                    offset = ycheat * xcur / xpos
                else:
                    offset = ycheat * (xtail - xcur) / (xtail - xpos)
                newtop.append( (xcur, ycur+offset) )
                if xnext != None and xcur < xpos-step and xnext > xpos+step:
                    # insert a point right at the cut so we can have a
                    # perfect fit
                    newtop.append( (xpos, ytop+ycheat) )
            for i, pt in enumerate(self.bottom):
                xcur = self.bottom[i][0]
                ycur = self.bottom[i][1]
                if i < len(self.bottom)-1:
                    xnext = self.bottom[i+1][0]
                else:
                    xnext = None
                if xcur < 0.0:
                    offset = 0.0
                elif xcur <= xpos:
                    offset = ycheat * xcur / xpos
                else:
                    offset = ycheat * (xtail - xcur) / (xtail - xpos)
                newbottom.append( (xcur, ycur-offset) )
                if xnext != None and xcur < xpos-step and xnext > xpos+step:
                    # insert a point right at the cut so we can have a
                    # perfect fit
                    newbottom.append( (xpos, ybottom-ycheat) )
            self.top = newtop
            self.bottom = newbottom
            # rebuild the polygon (which loses any cuts that might
            # have been made earlier, thus the note to do this first
            # if you want to force fit to trailing edge stock!)
            self.make_poly()

        # make the exact trailing edge stock shape
        p1 = (xtail, ytail)
        if shape == "Symmetrical":
            p2 = (xtail-width, ytail+h2)
            p3 = (xtail-width, ytail-h2)
        else:
            p2 = (xtail-width, ytail+height)
            p3 = (xtail-width, ytail)
        contour = Polygon.Polygon( (p1, p2, p3) )

        # make an oversize mask
        p1 = (xtail+width, ytail+h2)
        p2 = (xtail-width, ytail+height*2)
        p3 = (xtail-width, ytail-height*2)
        p4 = (xtail+width, ytail-h2)
        mask = Polygon.Polygon( (p1, p2, p3, p4) )

        if shape == "Flat Triangle":
            # need to prerotate to align mid line of stock with
            # midline of airfoil
            #print "prerotate = " + str( (h2, width) )
            preangle = math.atan2(h2, width)
            contour.rotate(preangle, xtail, ytail)
            mask.rotate(preangle, xtail, ytail)

        # rotate to best fit alignment
        contour.rotate(-angle, xtail, ytail)
        mask.rotate(-angle, xtail, ytail)

        # exact_shape = True can be a useful debugging tool because
        # you can see exactly the trailing edge part that gets cutout.
        exact_shape = False
        if exact_shape:
            self.poly = self.poly - contour
        else:
            self.poly = self.poly - mask

        result = []
        for p2 in contour[0]:
            p3 = (p2[0]+pos[1], pos[0]-nudge, p2[1])
            result.append(p3)
        return result

    # This version cuts a 'sheet' into the bottom trailing edge so the
    # bottom corner of the sheet cross section aligns with the tip of
    # the original airfoil and the bottom of the sheet follows the
    # bottom of the airfoil as best is possible.
    def cutout_trailing_edge_sheet(self, width=0.0, height=0.0, shape="",
                                   force_fit=True, pos=None, nudge=0.0):
        # make the Polygon representation of this part if needed
        if self.poly == None:
            self.make_poly()

        tn = len(self.top)
        bn = len(self.bottom)
        xnose = self.top[0][0]
        xtail = self.top[tn-1][0]
        yttail = self.top[tn-1][1]
        ybtail = self.bottom[bn-1][1]
        ytail = (yttail + ybtail) * 0.5
        chord = xtail - xnose
        if width > chord:
            # unable
            return

        step = 0.001
        xpos = xtail - step
        cur_dist = step
        # walk forward specified distances along the bottom curve
        # (starting at the back)
        ybottom = 0.0
        while cur_dist <= width and xpos >= xnose:
            ybottom = self.simple_interp(self.bottom, xpos)
            cur_dist = self.dist_2d( (xtail, ytail), (xpos, ybottom) )
            xpos -= step

        dx = xpos - xtail
        dy = ybottom - ytail
        print (dx, dy)
        angle = math.atan2(dy, -dx)
        print "angle = " + str(math.degrees(angle))

        #print "Trailing edge: stock height = " + str(height)
        #print "Rotated stock end height = " + str(height*math.cos(angle))
        #print "Rib height at cut pt = " + str(ytop - ybottom)

        # make the exact trailing edge stock shape
        p1 = (xtail, ytail)
        p2 = (xtail-width, ytail)
        p3 = (xtail-width, ytail+height)
        p4 = (xtail, ytail+height)
        contour = Polygon.Polygon( (p1, p2, p3, p4) )

        # make an oversize mask
        p1 = (xtail+width, ytail-height)
        p2 = (xtail-width, ytail-height)
        p3 = (xtail-width, ytail+height)
        p4 = (xtail+width, ytail+height)
        mask = Polygon.Polygon( (p1, p2, p3, p4) )

        # rotate to best fit alignment
        contour.rotate(-angle, xtail, ytail)
        mask.rotate(-angle, xtail, ytail)

        # exact_shape = True can be a useful debugging tool because
        # you can see exactly the trailing edge part that gets cutout.
        exact_shape = False
        if exact_shape:
            self.poly = self.poly - contour
        else:
            print "poly:", self.poly
            print "mask:", mask
            self.poly = self.poly - mask

        result = []
        for p2 in contour[0]:
            p3 = (p2[0]+pos[1], pos[0]-nudge, p2[1])
            result.append(p3)
        return result

# returns an airfoil that is 1.0-percent of af1 + percent of af2
def blend( af1, af2, percent ):
    result = Airfoil()
    result.name = "blend " + af1.name + " " + af2.name
    result.description = 'blend {:.2%}'.format(1.0-percent) + af1.description + ' + {:.2%}'.format(percent) + " " + af2.description

    n = len(af1.top)
    #print str(len(af1.top)) + " = " + str(len(af2.top))
    for i in range(0, n):
	y1 = af1.top[i][1]
	y2 = af2.top[i][1]
	y = (1.0-percent)*y1 + percent*y2
	result.top.append( (af1.top[i][0], y) )
    n = len(af1.bottom)
    #print str(len(af1.bottom)) + " = " + str(len(af2.bottom))
    for i in range(0, n):
	y1 = af1.bottom[i][1]
	y2 = af2.bottom[i][1]
	y = (1.0-percent)*y1 + percent*y2
	result.bottom.append( (af1.bottom[i][0], y) )
    result.raw_top = list(result.top)
    result.raw_bottom = list(result.bottom)
    return result

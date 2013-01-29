#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import fileinput
import math
import string

from contour import Contour
import spline

datapath = "../data"

class Airfoil(Contour):

    def __init__(self, name = "", samples = 0, use_spline = False):
        Contour.__init__(self)
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
        path = datapath + "/airfoils/" + base + ".dat"
        top = True
        dist = 0.0
        firstpt = True
        f = fileinput.input(path)
        for line in f:
            if f.isfirstline():
                self.description = string.join(line.split())
            else:
                xa, ya = line.split()
                x = float(xa)
                y = float(ya)
                #print str(x) + " " + str(y)
                if firstpt:
                    xlast = x
                    ylast = y
                    firstpt = False
                dist += self.dist_2d( (xlast, ylast), (x, y) )
                self.parax.append( (dist, x) )
                self.paray.append( (dist, y) )
                if top:
                    self.top.append( (x, y) )
                if x < 0.000001:
                    # mark the exact airfoil nose in parameterized
                    # surface distance space
                    self.nosedist = dist
                    top = False
                if not top:
                    self.bottom.append( (x, y) )
                xlast = x
                ylast = y
        self.top.reverse()
        if samples > 0:
            self.resample( samples, use_spline )

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
            if x >= 0.0:
                #print str(x) + " " + str(y)
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

    def cutout_leading_edge_diamond(self, size):
        target_diag = math.sqrt(2*size*size)
        # walk backwards equal amounts along both top and bottom curves until
        # find the first points that are diag apart.
        cur_diag = 0
        step = size / 1000
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
            # unable
            return
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

        # top skin
        newtop = []
        n = len(self.top)
        # skip cut out nose points
        i = 0
        while i < n and self.top[i][0] <= xtop:
            i += 1
        # 45 cutout
        newtop.append( corner )
        newtop.append( (xtop, ytop) )
        # remainder
        while i < n:
            newtop.append( self.top[i] )
            i += 1
        self.top = list(newtop)

        # bottom skin
        newbottom = []
        n = len(self.bottom)
        # skip cut out nose points
        i = 0
        while i < n and self.bottom[i][0] <= xbottom:
            i += 1
        # 45 cutout
        newbottom.append( corner )
        newbottom.append( (xbottom, ybottom) )
        # remainder
        while i < n:
            newbottom.append( self.bottom[i] )
            i += 1
        self.bottom = list(newbottom)

    def cutout_trailing_edge(self, width=0.0, height=0.0, shape="flat"):
        if shape == "flat":
            bottom_dist = width
            top_dist = math.sqrt(width*width + height+height)
        elif shape == "symmetrical":
            h2 = height*0.5
            bottom_dist = math.sqrt(width*width + h2*h2)
            top_dist = bottom_dist
        else:
            print "Unknown trailing edge shape. Must be 'flat' or 'symmetrical'"
            return

        n = len(self.top)
        xstart = self.top[0][0]
        xend = self.top[n-1][0]
        chord = xend - xstart
        if top_dist > chord or bottom_dist > chord:
            # unable
            return

        # walk forward specified distances along top and bottom curves
        xtop = self.walk_curve_from_back(self.top, xend, top_dist)
        ytop = self.simple_interp(self.top, xtop)
        xbottom = self.walk_curve_from_back(self.bottom, xend, bottom_dist)
        ybottom = self.simple_interp(self.bottom, xbottom)
        dy = ytop - ybottom
        print "Trailing edge: stock height = " + str(height) + " rib height = " + str(dy)

        #print (xtop, ytop)
        #print (xbottom, ybottom)
        dx = xtop - xbottom
        dy = ytop - ybottom
        #print (dx, dy)
        if math.fabs(dx) > 0.00001:
            slope = dy/dx
            #print "slope = " + str(slope)
            if math.fabs(slope) > 0.00001:
                b = ytop - slope*xtop
                #print "b = " + str(b)
                xint = -b / slope
                corner = ( xint, 0 )
            else:
                corner = ( (xtop+xbottom)*0.5, 0.0 )
        else:
            corner = ( xtop, 0.0 )
        #print "corner = " + str(corner)

        # top skin
        newtop = []
        n = len(self.top)
        # add lead points
        i = 0
        while i < n and self.top[i][0] < xtop:
            newtop.append( self.top[i] )
            i += 1
        # finish off the cut
        newtop.append( (xtop, ytop) )
        newtop.append( corner )
        self.top = list(newtop)

        # bottom skin
        newbottom = []
        n = len(self.bottom)
        # add lead points
        i = 0
        while i < n and self.bottom[i][0] < xbottom:
            newbottom.append( self.bottom[i] )
            i += 1
        # finish off the cut
        newbottom.append( (xbottom, ybottom) )
        newbottom.append( corner )
        self.bottom = list(newbottom)

# returns an airfoil that is 1.0-percent of af1 + percent of af2
def blend( af1, af2, percent ):
    result = Airfoil()
    result.name = "blend " + af1.name + " " + af2.name
    result.description = 'blend {:.2%}'.format(1.0-percent) + af1.description + ' + {:.2%}'.format(percent) + " " + af2.description

    n = len(af1.top)
    for i in range(0, n):
	y1 = af1.top[i][1]
	y2 = af2.top[i][1]
	y = (1.0-percent)*y1 + percent*y2
	result.top.append( (af1.top[i][0], y) )
    n = len(af1.bottom)
    for i in range(0, n):
	y1 = af1.bottom[i][1]
	y2 = af2.bottom[i][1]
	y = (1.0-percent)*y1 + percent*y2
	result.bottom.append( (af1.bottom[i][0], y) )
    result.raw_top = list(result.top)
    result.raw_bottom = list(result.bottom)
    return result

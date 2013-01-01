#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import fileinput
import math
import string
import spline

datapath = "../data"

class Airfoil:

    def __init__(self, name = "", samples = 0, use_spline = False):
        self.name = ""
        self.description = ""
        # parametric representation of the airfoil dist along surface
        # vs. x and vs. y
        self.parax = []
        self.paray = []
        self.top = []
        self.bottom = []
        self.nosedist = 0.0
        if ( name != "" ):
            self.load(name, samples, use_spline)

    def dist_2d(self, pt1, pt2):
        dx = pt2[0]-pt1[0]
        dy = pt2[1]-pt1[1]
        return math.sqrt(dx*dx + dy*dy)

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

    def simple_interp(self, points, v):
        index = spline.binsearch(points, v)
        n = len(points) - 1
        if index < n:
            xrange = points[index+1][0] - points[index][0]
            yrange = points[index+1][1] - points[index][1]
	    # print(" xrange = $xrange\n")
            percent = (v - points[index][0]) / xrange
	    # print(" percent = $percent\n")
            return points[index][1] + percent * yrange
        else:
            return points[index][1]

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

    def fit(self, maxpts = 30, maxerror = 0.1):
        self.top = list( self.curve_fit(self.top, maxpts, maxerror) )
        self.bottom = list( self.curve_fit(self.bottom, maxpts, maxerror) )

    def curve_fit(self, curve, maxpts = 30, maxerror = 0.1):
        wip = []

        # start with the end points
        n = len(curve)
        wip.append( curve[0] )
        wip.append( curve[n-1] )

        # iterate until termination conditions are met
        done = False
        while not done:
            maxy = 0
            maxx = 0
            maxdiff = 0
            maxi = -1
            # iterate over the orginal interior points
            for i in range(1, n-1):
                pt = curve[i]
                iy = self.simple_interp(wip, pt[0])
                diff = math.fabs(pt[1] - iy)
                if diff > maxdiff and diff > maxerror:
                    maxdiff = diff
                    maxi = i
                    maxx = pt[0]
                    maxy = pt[1]

            if maxi > -1:
                # found a match for a furthest off point
	        #print "($#wipx) inserting -> $maxx , $maxy at pos ";

                # find insertion point
                pos = 0
                wipn = len(wip)
                #print str(pos) + " " + str(wipn)
                while pos < wipn and maxx > wip[pos][0]:
                    pos += 1
                    #print pos
	        #print "$pos\n";
                wip.insert( pos, (maxx, maxy) )
            else:
                done = True

            if len(wip) >= maxpts:
                done = True

        return wip

    def display(self):
        for pt in self.top:
            print str(pt[0]) + " " + str(pt[1])
        for pt in self.bottom:
            print str(pt[0]) + " " + str(pt[1])

    def rotate_point( self, pt, angle ):
        rad = math.radians(angle)
        newx = pt[0] * math.cos(rad) - pt[1] * math.sin(rad)
        newy = pt[1] * math.cos(rad) + pt[0] * math.sin(rad)
        return (newx, newy)

    def rotate(self, angle):
        newtop = []
        newbottom = []
        for pt in self.top:
            newtop.append( self.rotate_point(pt, angle) )
        for pt in self.bottom:
            newbottom.append( self.rotate_point(pt, angle) )
        self.top = list(newtop)
        self.bottom = list(newbottom)

    def scale(self, hsize, vsize):
        newtop = []
        newbottom = []
        for pt in self.top:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            newtop.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            newbottom.append( (newx, newy) )
        self.top = list(newtop)
        self.bottom = list(newbottom)

    def move(self, x, y):
        newtop = []
        newbottom = []
        for pt in self.top:
            newx = pt[0] + x
            newy = pt[1] + y
            newtop.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] + x
            newy = pt[1] + y
            newbottom.append( (newx, newy) )
        self.top = list(newtop)
        self.bottom = list(newbottom)

    def walk_curve_dist(self, curve, xstart, target_dist):
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
            xtop = self.walk_curve_dist(self.top, xstart, dist)
            ytop = self.simple_interp(self.top, xtop)
            xbottom = self.walk_curve_dist(self.bottom, xstart, dist)
            ybottom = self.simple_interp(self.bottom, xbottom)
            cur_diag = self.dist_2d( (xtop, ytop), (xbottom, ybottom) )
            dist += step
        if dist >= chord:
            # unable
            return
        print (xtop, ytop)
        print (xbottom, ybottom)
        print (cur_diag, target_diag)
        dx = xtop - xbottom
        dy = ytop - ybottom
        angle = math.degrees(math.atan2(dy,dx))
        print angle
        a45 = angle + 45
        print a45
        r0 = self.rotate_point( (-size, 0), a45 )
        print r0
        corner = ( xtop + r0[0], ytop + r0[1] )
        print self.dist_2d( (xtop, ytop), corner )
        print self.dist_2d( corner, (xbottom, ybottom) )

        # top skin
        newtop = []
        n = len(self.top)
        # skip cut out nose points
        i = 0
        while self.top[i][0] <= xtop and i < n:
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
        while self.bottom[i][0] <= xbottom and i < n:
            i += 1
        # 45 cutout
        newbottom.append( corner )
        newbottom.append( (xbottom, ybottom) )
        # remainder
        while i < n:
            newbottom.append( self.bottom[i] )
            i += 1
        self.bottom = list(newbottom)

    # rel top/bottom, tangent/vertical, xpos, ysize
    def cutout(self, side = "top", orientation = "tangent", xpos = 0, xsize = 0, ysize = 0):

        top = False
        if side == "top":
            top = True

        tangent = False
        if orientation == "tangent":
            tangent = True;

        curve = []
        if top:
            curve = list(self.top)
        else:
            curve = list(self.bottom)

        n = len(curve)

        newcurve = []
        ypos = self.simple_interp(curve, xpos)

        angle = 0
        if tangent:
            slopes = spline.derivative1(curve)
            index = spline.binsearch(curve, xpos)
            slope = slopes[index]
            rad = math.atan2(slope,1)
            angle = math.degrees(rad)
        if not top:
            angle += 180
            if angle > 360:
                angle -= 360
        xhalf = xsize / 2
        r0 = self.rotate_point( (-xhalf, 0), angle )
        r1 = self.rotate_point( (-xhalf, -ysize), angle )
        r2 = self.rotate_point( (xhalf, -ysize), angle )
        r3 = self.rotate_point( (xhalf, 0), angle )
        if tangent:
            p0 = ( r0[0] + xpos, r0[1] + ypos )
            p1 = ( r1[0] + xpos, r1[1] + ypos )
            p2 = ( r2[0] + xpos, r2[1] + ypos )
            p3 = ( r3[0] + xpos, r3[1] + ypos )
        else:
            x = r0[0] + xpos
            p0 = ( r0[0] + xpos, self.simple_interp(curve, x) )
            p1 = ( r1[0] + xpos, r1[1] + ypos )
            p2 = ( r2[0] + xpos, r2[1] + ypos )
            x = r3[0] + xpos
            p3 = ( r3[0] + xpos, self.simple_interp(curve, x) )

        i = 0
        # nose portion
        while (curve[i][0] < p0[0] and curve[i][0] < p3[0]) and i < n:
            newcurve.append( curve[i] )
            i += 1
        # cut out
        if top:
            newcurve.append( p0 )
            newcurve.append( p1 )
            newcurve.append( p2 )
            newcurve.append( p3 )
        else:
            newcurve.append( p3 )
            newcurve.append( p2 )
            newcurve.append( p1 )
            newcurve.append( p0 )
        # skip airfoil coutout points
        while (curve[i][0] <= p0[0] or curve[i][0] <= p3[0]) and i < n:
            i += 1
        # tail portion
        while i < n:
            newcurve.append( curve[i] )
            i += 1
        if top:
            self.top = list(newcurve)
        else:
            self.bottom = list(newcurve)

    def cutout_stringer(self, side = "top", orientation = "tangent", xpos = 0, xsize = 0, ysize = 0):
        self.cutout(side, orientation, xpos, xsize, ysize)

    def add_build_tab(self, side = "top", xpos = 0, xsize = 0):
        # find the y value of the attach point and compute the size of
        # the tab needed
        bounds = self.get_bounds()
        if side == "top":
            ypos = self.simple_interp(self.top, xpos)
            ysize = bounds[1][1] - ypos
        else:
            ypos = self.simple_interp(self.bottom, xpos)
            ysize = ypos - bounds[0][1]
        self.cutout(side, "vertical", xpos, xsize, -ysize)

    def project_point(self, top, slopes, index, orig, ysize):
        slope = slopes[index]
        rad = math.atan2(slope,1)
        angle = math.degrees(rad)
        #print "xpos " + str(xpos) + " angle = " + str(angle)
        if not top:
            angle += 180
            if angle > 360:
                angle -= 360
        r0 = self.rotate_point( (0, ysize), angle )
        pt = ( r0[0] + orig[0], r0[1] + orig[1] )
        if top and pt[1] < 0.0:
            pt = (pt[0], 0.0)
        elif not top and pt[1] > 0.0:
            pt = (pt[0], 0.0)
        return pt

    def cutout_sweep(self, side = "top", xstart = 0, xsize = 0, ysize = 0):
        top = False
        if side == "top":
            top = True

        curve = []
        if top:
            curve = list(self.top)
        else:
            curve = list(self.bottom)

        n = len(curve)
        newcurve = []

        # nose portion
        i = 0
        while curve[i][0] < xstart and i < n:
            newcurve.append( curve[i] )
            i += 1

        # anchor sweep
        ypos = self.simple_interp(curve, xstart)
        newcurve.append( (xstart, ypos) )

        # sweep cutout
        slopes = spline.derivative1(curve)
        dist = 0.0
        xpos = xstart
        index = spline.binsearch(curve, xpos)
        first = True
        next_dist = 0
        while dist + next_dist <= xsize and index < n:
            dist += next_dist
            ypos = self.simple_interp(curve, xpos)
            pt = self.project_point(top, slopes, index, (xpos, ypos), -ysize)
            newcurve.append( pt )
            if index < n - 1:
                nextpt = curve[index+1]
                next_dist = self.dist_2d( (xpos, ypos), nextpt )
                xpos = nextpt[0]
            index += 1

        if index < n - 1:
            # finish sweep (advance x in proportion to get close to the
            # right total sweep dist
            rem = xsize - dist
            print "rem = " + str(rem)
            pct = rem / next_dist
            print "pct of next step = " + str(pct)
            xpos = curve[index-1][0]
            dx = curve[index][0] - xpos
            xpos += dx * rem
            ypos = self.simple_interp(curve, xpos)
            pt = self.project_point(top, slopes, index-1, (xpos, ypos), -ysize)
            newcurve.append( pt )
            newcurve.append( (xpos, ypos) )

        # tail portion
        while index < n:
            newcurve.append( curve[index] )
            index += 1

        if top:
            self.top = list(newcurve)
        else:
            self.bottom = list(newcurve)

    def get_bounds(self):
        if len(self.top) < 1:
            return ( (0,0), (0,0) )
        pt = self.top[0]
        minx = pt[0]
        maxx = pt[0]
        miny = pt[1]
        maxy = pt[1]
        for pt in self.top + self.bottom:
            if pt[0] < minx:
                minx = pt[0]
            if pt[0] > maxx:
                maxx = pt[0]
            if pt[1] < miny:
                miny = pt[1]
            if pt[1] > maxy:
                maxy = pt[1]
        return ( (minx, miny), (maxx, maxy) )

def blend( af1, af2, percent ):
    result = Airfoil()
    result.name = "blend " + af1.name + " " + af2.name
    result.description = 'blend {:.2%}'.format(percent) + af1.description + ' + {:.2%}'.format(1.0-percent) + " " + af2.description

    n = len(af1.top)
    for i in range(0, n):
	y1 = af1.top[i][1]
	y2 = af2.top[i][1]
	y = percent*y1 + (1.0-percent)*y2
	result.top.append( (af1.top[i][0], y) )
    n = len(af1.bottom)
    for i in range(0, n):
	y1 = af1.bottom[i][1]
	y2 = af2.bottom[i][1]
	y = percent*y1 + (1.0-percent)*y2
	result.bottom.append( (af1.bottom[i][0], y) )
    result.raw_top = list(result.top)
    result.raw_bottom = list(result.bottom)
    return result

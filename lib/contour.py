#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import fileinput
import math
import string
import spline


class Cutpos:
    def __init__(self, percent=None, front=None, rear=None, center=None, \
                     xpos=None):
        self.percent = percent             # placed at % point in chord
        self.front = front                 # dist from front of chord
        self.rear = rear                   # dist from rear of chord
        self.center = center               # dist from 25% chord if a
        self.xpos = xpos                   # not relative, just the actual pos

        # ypos + slope are defined, then the cut position will be at
        # the point the contour intesects the line that passes through
        # the xpos, ypos with the specified slope.  This is primarily
        # used to cut control surface clearance wedges.
        self.ypos = 0.0
        self.slope = 0.0

    # move the cutpos by dist amount
    def move(self, xdist=0.0):
        if self.percent != None:
            self.percent += xdist
        elif self.front != None:
            self.front += xdist
        elif self.rear != None:
            self.rear += xdist
        elif self.center != None:
            self.center += xdist
        elif self.xpos != None:
            self.xpos += xdist


class Cutout:
    def __init__(self, side="top", orientation="tangent", cutpos=None, \
                     xsize=0.0, ysize=0.0):
        # note: specify a value for only one of percent, front, rear, or center
        self.side = side                   # {top, bottom}
        self.orientation = orientation     # {tangent, vertical}
        self.xsize = xsize                 # horizontal size
        self.ysize = ysize                 # vertical size
        self.cutpos = cutpos               # Cutpos()


class Contour:

    def __init__(self):
        self.name = ""
        self.description = ""
        self.top = []
        self.bottom = []
        self.holes = []
        self.labels = []
        self.saved_bounds = []        # see self.save_bounds() for details

    def dist_2d(self, pt1, pt2):
        dx = pt2[0]-pt1[0]
        dy = pt2[1]-pt1[1]
        return math.sqrt(dx*dx + dy*dy)

    def simple_interp(self, points, v):
        index = spline.binsearch(points, v)
        n = len(points) - 1
        if index < n:
            xrange = points[index+1][0] - points[index][0]
            yrange = points[index+1][1] - points[index][1]
	    # print(" xrange = $xrange\n")
            if xrange > 0.0001:
                percent = (v - points[index][0]) / xrange
                # print(" percent = $percent\n")
                return points[index][1] + percent * yrange
            else:
                return points[index][1]
        else:
            return points[index][1]

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
        newholes = []
        newlabels = []
        for pt in self.top:
            newtop.append( self.rotate_point(pt, angle) )
        for pt in self.bottom:
            newbottom.append( self.rotate_point(pt, angle) )
        for hole in self.holes:
            newpt = self.rotate_point( (hole[0], hole[1]), angle)
            newholes.append( (newpt[0], newpt[1], hole[2]) )
        for label in self.labels:
            newpt = self.rotate_point( (label[0], label[1]), angle)
            newlabels.append( (newpt[0], newpt[1], label[2], label[3] + angle, label[4]) )
        self.top = list(newtop)
        self.bottom = list(newbottom)
        self.holes = list(newholes)
        self.labels = list(newlabels)

    def scale(self, hsize, vsize):
        newtop = []
        newbottom = []
        newholes = []
        newlabels = []
        for pt in self.top:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            newtop.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            newbottom.append( (newx, newy) )
        for hole in self.holes:
            newx = ( hole[0] * hsize )
            newy = ( hole[1] * vsize )
            if hsize <= vsize:
                newr = math.fabs( hole[2] * hsize )
            else:
                newr = math.fabs( hole[2] * vsize )
            newholes.append( (newx, newy, newr) )
        for label in self.labels:
            newx = ( label[0] * hsize )
            newy = ( label[1] * vsize )
            newlabels.append( (newx, newy, label[2], label[3], label[4]) )
        self.top = list(newtop)
        self.bottom = list(newbottom)
        self.holes = list(newholes)
        self.labels = list(newlabels)

    def move(self, x, y):
        newtop = []
        newbottom = []
        newholes = []
        newlabels = []
        for pt in self.top:
            newx = pt[0] + x
            newy = pt[1] + y
            newtop.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] + x
            newy = pt[1] + y
            newbottom.append( (newx, newy) )
        for hole in self.holes:
            newx = hole[0] + x
            newy = hole[1] + y
            newholes.append( (newx, newy, hole[2]) )
        for label in self.labels:
            newx = label[0] + x
            newy = label[1] + y
            newlabels.append( (newx, newy, label[2], label[3], label[4]) )
        self.top = list(newtop)
        self.bottom = list(newbottom)
        self.holes = list(newholes)
        self.labels = list(newlabels)

    # the saved "bounds" are used cooperatively to mark the size of
    # the part before any leading/trailing edge cutouts so that these
    # cuts don't cause us to lose the original size of the part and
    # our cut positions can remain constant through out the build
    # process.
    def save_bounds(self):
        self.saved_bounds = self.get_bounds()

    # given one of the possible ways to specify position, return the
    # actual position (relative to the original pre-cut part dimensions)
    def get_xpos(self, cutpos):
        if len(self.saved_bounds) == 0:
            print "need to call contour.save_bounds() after part created,"
            print "but before any cutouts are made"
            self.save_bounds()
        chord = self.saved_bounds[1][0] - self.saved_bounds[0][0]
        if cutpos.percent != None:
            xpos = self.saved_bounds[0][0] + chord * cutpos.percent
        elif cutpos.front != None:
            xpos = self.saved_bounds[0][0] + cutpos.front
        elif cutpos.rear != None:
            xpos = self.saved_bounds[1][0] - cutpos.rear
        elif cutpos.center != None:
            ctrpt = self.saved_bounds[0][0] + chord * 0.25
            xpos = ctrpt + cutpos.center
        elif cutpos.xpos != None:
            xpos = cutpos.xpos
        return xpos

    # trim everything front or rear of a given position
    def trim(self, side="top", discard="rear", cutpos=None):
        if side == "top":
            curve = list(self.top)
        else:
            curve = list(self.bottom)
        newcurve = []
        xpos = self.get_xpos(cutpos)
        ypos = self.simple_interp(curve, xpos)
        n = len(curve)
        i = 0
        if discard == "rear":
            # copy up to the cut point
            while i < n and curve[i][0] <= xpos:
                newcurve.append( curve[i] )
                i += 1
            if i < n:
                newcurve.append( (xpos, ypos) )
        else:
            # skip to the next point after the cut
            while i < n and curve[i][0] < xpos:
                #print "i=" + str(i) + " n=" + str(n) + " curve[i][0]=" + str(curve[i][0]) + " xpos=" + str(xpos)
                i += 1
            if i > 0:
                newcurve.append( (xpos, ypos) )
                #print "add=" + str( (xpos, ypos) )
            while i < n:
                newcurve.append( curve[i] )
                #print "add=" + str(curve[i])
                i += 1
        if side == "top":
            self.top = list(newcurve)
        else:
            self.bottom = list(newcurve)
 
    # side={top,bottom} (attached to top or bottom of airfoil)
    # orientation={tangent,vertical} (aligned vertically or flush with surface)
    # xpos={percent,front,rear,zero} (position is relative to percent of chord,
    #      distance from front, distance from rear, or distance from center 
    #      (25% chord point)
    # xsize=value (horizontal size of cutout)
    # ysize=value (vertical size)

    # use side="bottom" + ysize=-negative_value +
    # orientation="vertical" for build support tabs
    def cutout(self, cutout):
        if len(self.saved_bounds) == 0:
            print "need to call contour.save_bounds() after part created,"
            print "but before any cutouts are made"
            self.save_bounds()
        top = False
        if cutout.side == "top":
            top = True

        tangent = False
        if cutout.orientation == "tangent":
            tangent = True;

        # compute position of cutout
        xpos = self.get_xpos(cutout.cutpos)

        # sanity check
        bounds = self.get_bounds()
        if xpos < bounds[0][0] or xpos > bounds[1][0]:
            print "cutout is outside of part"
            return
        else:
            print "bounds = " + str(bounds) + " xpos = " + str(xpos)

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
        xhalf = cutout.xsize / 2
        r0 = self.rotate_point( (-xhalf, 0), angle )
        r1 = self.rotate_point( (-xhalf, -cutout.ysize), angle )
        r2 = self.rotate_point( (xhalf, -cutout.ysize), angle )
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
        while i < n and (curve[i][0] < p0[0] and curve[i][0] < p3[0]):
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
        while i < n and (curve[i][0] <= p0[0] or curve[i][0] <= p3[0]):
            i += 1
        # tail portion
        while i < n:
            newcurve.append( curve[i] )
            i += 1
        if top:
            self.top = list(newcurve)
        else:
            self.bottom = list(newcurve)
        # finally trim to the original part size
        front = Cutpos(xpos=self.saved_bounds[0][0])
        rear = Cutpos(xpos=self.saved_bounds[1][0])
        self.trim(side="top", discard="front", cutpos=front)
        self.trim(side="bottom", discard="front", cutpos=front)
        self.trim(side="top", discard="rear", cutpos=rear)
        self.trim(side="bottom", discard="rear", cutpos=rear)

    def cutout_stringer(self, stringer):
        self.cutout( stringer )

    def add_build_tab(self, side = "top", percent=None, front=None, \
                          rear=None, center=None, \
                          xsize = 0, yextra = 0):
        # compute actual "x" position
        xpos = self.get_xpos(cutout.cutpos)

        # get current bounds
        bounds = self.get_bounds()

        # find the y value of the attach point and compute the
        # vertical size of the tab needed
        if side == "top":
            ypos = self.simple_interp(self.top, xpos)
            ysize = bounds[1][1] - ypos + yextra
        else:
            ypos = self.simple_interp(self.bottom, xpos)
            ysize = ypos - bounds[0][1] + yextra

        # call the cutout method with negative ysize to create a tab
        self.cutout(side, orientation="vertical", percent=percent, \
                        front=front, rear=rear, center=center, \
                        xsize=xsize, ysize=-ysize)

    def add_hole(self, xpos, ypos, radius):
        self.holes.append( (xpos, ypos, radius) )        

    def add_label(self, xpos, ypos, size, rotate, text):
        self.labels.append( (xpos, ypos, size, rotate, text) )        

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

    def cutout_sweep(self, side="top", xstart=0, xsize=0, ysize=0):
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
        while i < n and curve[i][0] < xstart:
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
        while index < n and dist + next_dist <= xsize:
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
            #print "rem = " + str(rem)
            pct = rem / next_dist
            #print "pct of next step = " + str(pct)
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

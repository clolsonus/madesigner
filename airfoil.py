#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import fileinput
import math
import string
import spline

datapath = "./data"

class Airfoil:

    def __init__(self, name = "", samples = 0, use_spline = False):
        self.name = ""
        self.description = ""
        self.raw_top = []
        self.raw_bottom = []
        self.top = []
        self.bottom = []
        if ( name != "" ):
            self.load(name, samples, use_spline)

    def load(self, base, samples = 0, use_spline = False):
        self.name = base
        path = datapath + "/airfoils/" + base + ".dat"
        top = True
        for line in fileinput.input(path):
            if fileinput.isfirstline():
                self.description = string.join(line.split())
            else:
                xa, ya = line.split()
                x = float(xa)
                y = float(ya)
                if top:
                    self.raw_top.append( (x,y) )
                if x < 0.000001:
                    top = not top
                if not top:
                    self.raw_bottom.append( (x,y) )
                # print "x = " + str(x) + " y = " + str(y)
        self.raw_top.reverse()
        # print self.description + " (" + self.name + ") Loaded " + str(len(self.top) + len(self.bottom)) + " points"
        if samples > 0:
            self.resample( samples, use_spline )
        else:
            self.top = list(self.raw_top)
            self.bottom = list(self.raw_bottom)

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
        step = 1.0 / xdivs
        top_y2 = spline.derivative2( self.raw_top )
        bottom_y2 = spline.derivative2( self.raw_bottom )
        for i in range(0, xdivs+1):
            x = i * step
            if use_spline:
                index = spline.binsearch(self.raw_top, x)
                y = spline.spline(self.raw_top, top_y2, index, x)
                #print str(index) + " " + str(y)
            else:
                y = self.simple_interp(self.raw_top, x )
            self.top.append( (x, y) )

        for i in range(0, xdivs+1):
            x = i * step
            if use_spline:
                index = spline.binsearch(self.raw_bottom, x)
                y = spline.spline(self.raw_bottom, bottom_y2, index, x)
            else:
                y = self.simple_interp(self.raw_bottom, x )
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
                while maxx > wip[pos][0] and pos < wipn:
                    pos += 1
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

    # rel top/bottom, abs x,y, tangent y/n
    def cutout_stringer(self, side = "top", orientation = "tangent", xpos = 0, xsize = 0, ysize = 0):

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

    def cutout_sweep(self, side = "top", xstart = 0, xsize = 0, ysize = 0, xstep = 1.0):
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
        first = True
        while dist <= xsize:
            ypos = self.simple_interp(curve, xpos)
            index = spline.binsearch(curve, xpos)
            slope = slopes[index]
            rad = math.atan2(slope,1)
            angle = math.degrees(rad)
            #print "xpos " + str(xpos) + " angle = " + str(angle)
            if not top:
                angle += 180
                if angle > 360:
                    angle -= 360
            r0 = self.rotate_point( (0, -ysize), angle )
            pt = ( r0[0] + xpos, r0[1] + ypos )
            newcurve.append( pt )
            if first:
                last_pt = (xpos, ypos)
                first = False
            dx = last_pt[0] - xpos
            dy = last_pt[1] - ypos
            d = math.sqrt(dx*dx + dy*dy)
            dist += d
            #print "d = " + str(d) + " dist = " + str(dist)
            last_pt = (xpos, ypos)
            xpos += xstep

        # finish sweep
        xpos -= xstep
        ypos = self.simple_interp(curve, xpos)
        newcurve.append( (xpos, ypos) )

        # skip airfoil coutout points
        while curve[i][0] <= xpos and i < n:
            i += 1

        # tail portion
        while i < n:
            newcurve.append( curve[i] )
            i += 1

        if top:
            self.top = list(newcurve)
        else:
            self.bottom = list(newcurve)

def blend( af1, af2, percent ):
    result = Airfoil()
    result.name = "blend " + af1.name + " " + af2.name
    result.description = "blend " + str(percent) + " " + af1.description + " " + str(1.0-percent) + " " + af2.description

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

#root = Airfoil("clarky")
#tip = Airfoil("arad6")
#root.display()
#tip.display()

#root_smooth = root.resample(1000, True)
#tip_smooth = tip.resample(1000, False)
#root_smooth.display()
#tip_smooth.display()

#blend1 = blend( root_smooth, tip_smooth, 1.0 )
#blend2 = blend( root_smooth, tip_smooth, 0.5 )
#blend3 = blend( root_smooth, tip_smooth, 0.0 )
#blend1.display()
#blend2.display()
#blend3.display()

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

    def __init__(self, name = ""):
        self.name = ""
        self.description = ""
        self.top = []
        self.bottom = []
        if ( name != "" ):
            self.load(name)

    def load(self, base):
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
                    self.top.append( (x,y) )
                if x < 0.000001:
                    top = not top
                if not top:
                    self.bottom.append( (x,y) )
                # print "x = " + str(x) + " y = " + str(y)
        self.top.reverse()
        # print self.description + " (" + self.name + ") Loaded " + str(len(self.top) + len(self.bottom)) + " points"

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
        result = Airfoil()
        result.name = self.name
        result.description = self.description
        step = 1.0 / xdivs
        top_y2 = spline.derivative2( self.top )
        bottom_y2 = spline.derivative2( self.bottom )
        for i in range(0, xdivs+1):
            x = i * step
            if use_spline:
                index = spline.binsearch(self.top, x)
                y = spline.spline(self.top, top_y2, index, x)
                #print str(index) + " " + str(y)
            else:
                y = self.simple_interp(self.top, x )
            result.top.append( (x, y) )

        for i in range(0, xdivs+1):
            x = i * step
            if use_spline:
                index = spline.binsearch(self.bottom, x)
                y = spline.spline(self.bottom, bottom_y2, index, x)
            else:
                y = self.simple_interp(self.bottom, x )
            result.bottom.append( (x, y) )
        return result

    def display(self):
        for pt in self.top:
            print str(pt[0]) + " " + str(pt[1])
        for pt in self.bottom:
            print str(pt[0]) + " " + str(pt[1])

    def rotate(self, angle):
        result = Airfoil()
        result.name = self.name
        result.description = self.description + " rotated by " + str(angle) + " degrees"
        rad = math.radians(angle)
        for pt in self.top:
            newx = pt[0] * math.cos(rad) - pt[1] * math.sin(rad)
            newy = pt[1] * math.cos(rad) + pt[0] * math.sin(rad)
            result.top.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] * math.cos(rad) - pt[1] * math.sin(rad)
            newy = pt[1] * math.cos(rad) + pt[0] * math.sin(rad)
            result.bottom.append( (newx, newy) )
        return result

    def scale(self, hsize, vsize):
        result = Airfoil()
        result.name = self.name
        result.description = self.description + " scaled by " + str(hsize) + "," + str(vsize)
        for pt in self.top:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            result.top.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            result.bottom.append( (newx, newy) )
        return result

    def move(self, x, y):
        result = Airfoil()
        result.name = self.name
        result.description = self.description + " moved by " + str(x) + "," + str(y)
        for pt in self.top:
            newx = pt[0] + x
            newy = pt[1] + y
            result.top.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] + x
            newy = pt[1] + y
            result.bottom.append( (newx, newy) )
        return result

    # rel top/bottom, abs x,y, tangent y/n
    def cutout_rel(self, top, xpos, xsize, ysize):
        result = Airfoil()
        result.name = self.name
        result.description = self.description
        xhalf = xsize / 2
        xstart = xpos - xhalf
        xend = xpos + xhalf
        # top segment
        if top:
            n = len(self.top)
            ytop = self.simple_interp(self.top, xpos)
            i = 0
            # nose portion
            while self.top[i][0] < xstart and i < n:
                result.top.append( self.top[i] )
                i += 1
            # cut out
            ystart = self.simple_interp(self.top, xstart)
            yend = self.simple_interp(self.top, xstart)
            result.top.append( (xstart, ystart) )
            result.top.append( (xstart, ytop - ysize) )
            result.top.append( (xend, ytop - ysize) )
            result.top.append( (xend, yend) )
            # skip airfoil coutout points
            while self.top[i][0] <= xend and i < n:
                i += 1
            # tail portion
            while i < n:
                result.top.append( self.top[i] )
                i += 1
        else:
            result.top = self.top
        # bottom segment
        if top:
            result.bottom = self.bottom
        else:
            n = len(self.bottom)
            ybottom = self.simple_interp(self.bottom, xpos)
            i = 0
            # nose portion
            while self.bottom[i][0] < xstart and i < n:
                result.bottom.append( self.bottom[i] )
                i += 1
            # cut out
            ystart = self.simple_interp(self.bottom, xstart)
            yend = self.simple_interp(self.bottom, xstart)
            result.bottom.append( (xstart, ystart) )
            result.bottom.append( (xstart, ybottom + ysize) )
            result.bottom.append( (xend, ybottom + ysize) )
            result.bottom.append( (xend, yend) )
            # skip airfoil coutout points
            while self.bottom[i][0] <= xend and i < n:
                i += 1
            # tail portion
            while i < n:
                result.bottom.append( self.bottom[i] )
                i += 1

        return result

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

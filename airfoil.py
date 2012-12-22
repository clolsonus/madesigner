#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import fileinput
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
        path = datapath + "/airfoils/" + base + ".dat";
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
                # print "x = " + str(x) + " y = " + str(y);
        self.top.reverse()
        print self.description + " (" + self.name + ") Loaded " + str(len(self.top) + len(self.bottom)) + " points"

    def simple_interp(self, points, v):
        index = spline.binsearch(points, v)
        n = len(points) - 1
        if index < n:
            xrange = points[index+1][0] - points[index][0]
            yrange = points[index+1][1] - points[index][1]
	    # print(" xrange = $xrange\n");
            percent = (v - points[index][0]) / xrange
	    # print(" percent = $percent\n");
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


def airfoil_blend( af1, af2, percent ):
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

root = Airfoil("clarky");
tip = Airfoil("arad6");
#root.display()
#tip.display()

root_smooth = root.resample(1000, True)
tip_smooth = tip.resample(1000, False)
#root_smooth.display()
#tip_smooth.display()

blend1 = airfoil_blend( root_smooth, tip_smooth, 1.0 )
blend2 = airfoil_blend( root_smooth, tip_smooth, 0.5 )
blend3 = airfoil_blend( root_smooth, tip_smooth, 0.0 )
blend1.display()
blend2.display()
blend3.display()

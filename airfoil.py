#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import fileinput
import string

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


root = Airfoil("clarky");
tip = Airfoil("arad6");

#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import fileinput
import math
import string
import spline
import Polygon
import Polygon.Shapes
import Polygon.Utils


class Cutpos:
    def __init__(self, percent=None, front=None, rear=None, \
                     xpos=None, atstation=None, slope=None):
        self.percent = percent             # placed at % point in chord
        self.front = front                 # dist from front of chord
        self.rear = rear                   # dist from rear of chord
        self.xpos = xpos                   # abs position

        # if atstation + slope are defined, then the cut position will
        # be just like any other cut position at the 'root' station,
        # but offset by dist+slope for any other station.  This allows
        # straight stringers or aileron cut at arbitray angles
        # relative to the rest of the wing.
        self.atstation = atstation
        self.slope = slope

    # move the cutpos by dist amount
    def move(self, xdist=0.0):
        if self.percent != None:
            self.percent += xdist
        elif self.front != None:
            self.front += xdist
        elif self.rear != None:
            self.rear += xdist
        elif self.xpos != None:
            self.xpos += xdist


class Cutout:
    def __init__(self, surf="top", orientation="tangent", cutpos=None, \
                     xsize=0.0, ysize=0.0):
        # note: specify a value for only one of percent, front, rear, or xpos
        self.surf = surf                   # {top, bottom}
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
        self.poly = None
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

    def poly_intersect(self, surf="top", xpos=0.0):
        if self.poly == None:
            self.make_poly()

        ymin = None
        ymax = None
        for contour in self.poly:
            # print "contour " + str(contour)
            p0 = None
            for p1 in contour:
                # print " p1 = " + str(p1) + " xpos = " + str(xpos)
                if p0 != None:
                    if p0[0] < p1[0]:
                        a = p0
                        b = p1
                    else:
                        a = p1
                        b = p0
                    if a[0] <= xpos and b[0] >= xpos:
                        # print "found a spanning segment!"
                        # a & b span xpos
                        xrange = b[0] - a[0]
                        yrange = b[1] - a[1]
                        if xrange > 0.0001:
                            percent = (xpos - a[0]) / xrange
                            ypos= a[1] + percent * yrange
                        else:
                            ypos = a[1]
                        if ymin == None or ypos < ymin:
                            ymin = ypos
                        if ymax == None or ypos > ymax:
                            ymax = ypos
                p0 = p1

            if surf == "top":
                return ymax
            else:
                return ymin
                    
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

    # rotate a point about (0, 0)
    def rotate_point( self, pt, angle ):
        rad = math.radians(angle)
        newx = pt[0] * math.cos(rad) - pt[1] * math.sin(rad)
        newy = pt[1] * math.cos(rad) + pt[0] * math.sin(rad)
        return (newx, newy)

    def rotate(self, angle):
        newtop = []
        newbottom = []
        newlabels = []
        for pt in self.top:
            newtop.append( self.rotate_point(pt, angle) )
        for pt in self.bottom:
            newbottom.append( self.rotate_point(pt, angle) )
        for label in self.labels:
            newpt = self.rotate_point( (label[0], label[1]), angle)
            newlabels.append( (newpt[0], newpt[1], label[2], label[3] + angle, label[4]) )
        if self.poly != None:
            self.poly.rotate(math.radians(angle), 0.0, 0.0)
        self.top = list(newtop)
        self.bottom = list(newbottom)
        self.labels = list(newlabels)

    def scale(self, hsize, vsize):
        newtop = []
        newbottom = []
        newlabels = []
        for pt in self.top:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            newtop.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] * hsize
            newy = pt[1] * vsize
            newbottom.append( (newx, newy) )
        for label in self.labels:
            newx = ( label[0] * hsize )
            newy = ( label[1] * vsize )
            newlabels.append( (newx, newy, label[2], label[3], label[4]) )
        self.top = list(newtop)
        self.bottom = list(newbottom)
        self.labels = list(newlabels)

    def move(self, x, y):
        newtop = []
        newbottom = []
        newlabels = []
        for pt in self.top:
            newx = pt[0] + x
            newy = pt[1] + y
            newtop.append( (newx, newy) )
        for pt in self.bottom:
            newx = pt[0] + x
            newy = pt[1] + y
            newbottom.append( (newx, newy) )
        for label in self.labels:
            newx = label[0] + x
            newy = label[1] + y
            newlabels.append( (newx, newy, label[2], label[3], label[4]) )
        self.top = list(newtop)
        self.bottom = list(newbottom)
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
    def get_xpos(self, cutpos=None, station=None):
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
        elif cutpos.xpos != None:
            xpos = cutpos.xpos
        else:
            print "get_xpos() called with no valid cut position!!!"
        if cutpos.atstation != None and station != None:
            if cutpos.slope == None:
                cutpos.slope = 0.0
            lat_dist = math.fabs(station) - cutpos.atstation
            long_dist = lat_dist * cutpos.slope
            xpos += long_dist
        return xpos

    # given a line (point + slope) return the "xpos" of the
    # intersection with the contour (does not handle the special case
    # of a vertical slope in either line)
    def intersect(self, surf="top", pt=None, slope=None):
        if surf == "top":
            curve = list(self.top)
        else:
            curve = list(self.bottom)
        m1 = slope
        b1 = pt[1] - m1 * pt[0]
        n = len(curve)
        i = 0
        found = False
        while i < n+1 and not found:
            pt1 = curve[i]
            pt2 = curve[i+1]
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            if math.fabs(dx) > 0.0001:
                m2 = dy / dx
                b2 = pt1[1] - m2 * pt1[0]
                if math.fabs(m1 - m2) > 0.0001:
                    x = (b2 - b1) / (m1 - m2)
                    if x >= pt1[0] and x <= pt2[0]:
                        found = True
                else:
                    print "parallel lines"
            else:
                print "vertical segment"
            i += 1
        if found:
            return x
        else:
            return None

    # trim everything front or rear of a given position
    def trim(self, surf="top", discard="rear", cutpos=None, station=None):
        if surf == "top":
            curve = list(self.top)
        else:
            curve = list(self.bottom)
        newcurve = []
        xpos = self.get_xpos(cutpos, station)
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
        if surf == "top":
            self.top = list(newcurve)
        else:
            self.bottom = list(newcurve)
 
    # build the Polygon representation of the shape from the
    # top/bottom curves.  The Polygon representation is used for doing
    # all the cutouts once the basic shape is created.  The Polygon
    # form can also spit out try strips and do a few other tricks that
    # are handy later on.
    def make_poly(self):
        reverse_top = list(self.top)
        reverse_top.reverse()
        shape = reverse_top + self.bottom
        self.poly = Polygon.Polygon(shape)
        # todo: add holes (should be easy, but want to work on other
        # aspects first)
        
    # surf={top,bottom} (attached to top or bottom of airfoil)
    # orientation={tangent,vertical} (aligned vertically or flush with surface)
    # xpos={percent,front,rear,xpos} (position is relative to percent of chord,
    #      distance from front, distance from rear, or distance from chord
    #      zero point)
    # xsize=value (horizontal size of cutout)
    # ysize=value (vertical size)
    def cutout(self, cutout, pos=None, nudge=0.0):
        if len(self.saved_bounds) == 0:
            print "need to call contour.save_bounds() after part created,"
            print "but before any cutouts are made"
            self.save_bounds()

        tangent = False
        if cutout.orientation == "tangent":
            tangent = True;

        # make the Polygon representation of this part if needed
        if self.poly == None:
            self.make_poly()

        # compute position of cutout
        xpos = self.get_xpos(cutout.cutpos, station=pos[0])
        ypos = self.poly_intersect(cutout.surf, xpos)

        # make, position, and orient the cutout
        angle = 0
        if tangent:
            if cutout.surf == "top":
                curve = list(self.top)
            else:
                curve = list(self.bottom)
            slopes = spline.derivative1(curve)
            index = spline.binsearch(curve, xpos)
            slope = slopes[index]
            rad = math.atan2(slope,1)
            angle = math.degrees(rad)
        if cutout.surf != "top":
            angle += 180
            if angle > 360:
                angle -= 360
        xhalf = cutout.xsize / 2
        yhalf = cutout.ysize / 2
        # extend mask shape by yhalf past boundary so we get a clean cutout
        # with no "flash"
        r0 = self.rotate_point( (-xhalf, yhalf), angle )
        r1 = self.rotate_point( (-xhalf, -cutout.ysize), angle )
        r2 = self.rotate_point( (xhalf, -cutout.ysize), angle )
        r3 = self.rotate_point( (xhalf, yhalf), angle )
        p0 = ( r0[0] + xpos, r0[1] + ypos )
        p1 = ( r1[0] + xpos, r1[1] + ypos )
        p2 = ( r2[0] + xpos, r2[1] + ypos )
        p3 = ( r3[0] + xpos, r3[1] + ypos )
        mask = Polygon.Polygon( (p0, p1, p2, p3) )
        self.poly = self.poly - mask

        # also make the true shape while we are here (reusing the
        # bottom of the cut mask)
        r0 = self.rotate_point( (-xhalf, 0.0), angle )
        r3 = self.rotate_point( (xhalf, 0.0), angle )
        p0 = ( r0[0] + xpos, r0[1] + ypos )
        p3 = ( r3[0] + xpos, r3[1] + ypos )
        v0 = ( p0[0]+pos[1], pos[0]-nudge, p0[1] )
        v1 = ( p1[0]+pos[1], pos[0]-nudge, p1[1] )
        v2 = ( p2[0]+pos[1], pos[0]-nudge, p2[1] )
        v3 = ( p3[0]+pos[1], pos[0]-nudge, p3[1] )
        shape = (v0, v1, v2, v3)
        return shape

    # build tab
    def buildtab(self, cutout, station=None):
        if len(self.saved_bounds) == 0:
            print "need to call contour.save_bounds() after part created,"
            print "but before any cutouts are made"
            self.save_bounds()
        top = False
        if cutout.surf == "top":
            top = True

        # no support of tangent build tabs

        # make the Polygon representation of this part if needed
        if self.poly == None:
            self.make_poly()

        if top:
            curve = list(self.top)
        else:
            curve = list(self.bottom)

        # compute base position of cutout
        xpos = self.get_xpos(cutout.cutpos, station=station)
        ypos = self.simple_interp(curve, xpos)

        xhalf = cutout.xsize / 2
        x1 = xpos - xhalf
        x2 = xpos + xhalf
        y1 = self.simple_interp(curve, x1)
        y2 = self.simple_interp(curve, x2)
        ybase = y1
        if top:
            if y2 < y1:
                ybase = y2
        else:
            if y2 > y1:
                ybase = y2

        # make the tab
        p0 = (x1, ybase)
        if top:
            p1 = (x1, ypos + cutout.ysize)
            p2 = (x2, ypos + cutout.ysize)
        else:
            p1 = (x1, ypos - cutout.ysize)
            p2 = (x2, ypos - cutout.ysize)
        p3 = (x2, ybase)

        tab = Polygon.Polygon( (p0, p1, p2, p3) )
        self.poly = self.poly + tab


    def cutout_stringer(self, stringer, pos=None, nudge=0.0):
        return self.cutout( stringer, pos=pos, nudge=nudge )

    def add_build_tab(self, surf="top", cutpos=None, \
                          xsize=0.0, yextra=0.0):
        # compute actual "x" position
        xpos = self.get_xpos(cutpos)

        # get current bounds
        bounds = self.get_bounds()

        # find the y value of the attach point and compute the
        # vertical size of the tab needed
        if surf == "top":
            ypos = self.simple_interp(self.top, xpos)
            ysize = bounds[1][1] - ypos + yextra
        else:
            ypos = self.simple_interp(self.bottom, xpos)
            ysize = ypos - bounds[0][1] + yextra

        cutout = Cutout( surf=surf, orientation="vertical", \
                             cutpos=cutpos, \
                             xsize=xsize, ysize=ysize )

        # call the cutout method with negative ysize to create a tab
        self.buildtab(cutout)

    def cut_hole(self, xpos, ypos, radius):
        if self.poly == None:
            self.make_poly()
        hole = Polygon.Shapes.Circle(radius=radius, center=(xpos, ypos), \
                                         points=32)
        self.poly = self.poly - hole

    def add_label(self, xpos, ypos, size, rotate, text):
        self.labels.append( (xpos, ypos, size, rotate, text) )        

    def project_point(self, orig, ysize, surf, slope):
        rad = math.atan2(slope,1)
        angle = math.degrees(rad)
        #print "xpos " + str(xpos) + " angle = " + str(angle)
        if surf == "top":
            angle += 180
            if angle > 360:
                angle -= 360
        r0 = self.rotate_point( (0, ysize), angle )
        pt = ( r0[0] + orig[0], r0[1] + orig[1] )
        return pt

    def project_contour(self, surf="top", \
                            xstart=0, xend=None, xdist=None, \
                            ysize=0):
        #print "xstart=" + str(xstart) + " xend=" + str(xend) + " xdist=" + str(xdist)
        curve = []
        #print "surf == " + surf
        if surf == "top":
            curve = list(self.top)
        else:
            curve = list(self.bottom)

        n = len(curve)
        slopes = spline.derivative1(curve)
        shape = []

        # make the exact sweep base line
        dist = 0.0
        xpos = xstart
        ypos = self.simple_interp(curve, xstart)
        shape.append( (xpos, ypos) )
        index = spline.binsearch(curve, xpos)
        if curve[index][0] <= xpos:
            index += 1
        next_dist = 0
        done = False
        #while index < n and dist + next_dist <= xdist:
        while index < n and not done:
            nextpt = curve[index]
            next_dist = self.dist_2d( (xpos, ypos), nextpt )
            if (xdist and dist + next_dist <= xdist) or \
                    (xend and nextpt[0] <= xend):
                dist += next_dist
                xpos = nextpt[0]
                ypos = nextpt[1]
                shape.append( (xpos, ypos) )
                index += 1
            else:
                done = True

        # add the final point of the curve (if needed)
        if index < n and xdist and dist < xdist:
            rem = xdist - dist
            #print "rem = " + str(rem)
            pct = rem / next_dist
            #print "pct of next step = " + str(pct)
            dx = nextpt[0] - xpos
            xpos += dx * pct
            ypos = self.simple_interp(curve, xpos)
            shape.append( (xpos, ypos) )
        elif index < n and xend and xpos < xend:
            xpos = xend
            ypos = self.simple_interp(curve, xpos)
            shape.append( (xpos, ypos) )

        # project the sweep line at the specified thickness
        result = []
        for p in shape:
            index = spline.binsearch(curve, p[0])
            slope = slopes[index]
            proj = self.project_point(p, ysize, surf, slope)
            result.append(proj)

        return result

    def cutout_sweep(self, surf="top", xstart=0.0, \
                         xend=None, xdist=None, ysize=0.0, pos=None, nudge=0.0):
        if self.poly == None:
            self.make_poly()
        flush = self.project_contour(surf=surf, xstart=xstart, \
                                        xend=xend, xdist=xdist, \
                                        ysize=0.0)
        surf1 = self.project_contour(surf=surf, xstart=xstart, \
                                         xend=xend, xdist=xdist, \
                                         ysize=-ysize)
        surf2 = self.project_contour(surf=surf, xstart=xstart, \
                                         xend=xend, xdist=xdist, \
                                         ysize=ysize)
        surf1.reverse()
        shape = surf1 + surf2
        mask = Polygon.Polygon(shape)
        self.poly = self.poly - mask

        # generate 3d points as top surface and bottom surface
        top = []
        for p2 in flush:
            v3 = (p2[0]+pos[1], pos[0]-nudge, p2[1])
            top.append(v3)
        bot =[]
        for p2 in surf2:
            v3 = (p2[0]+pos[1], pos[0]-nudge, p2[1])
            bot.append(v3)
        return (top, bot)

    # quick scan polygons for possible degenerate problems.  these can
    # occur due to odd numerical issues when we pile a lot of stuff on
    # top of each other close together.
    def reduce_degeneracy(self, poly):
        result = Polygon.Polygon()
        for c in poly:
            # look for simple out and backs (zero width peninsula)
            shape1 = []
            n = len(c)
            shape1.append(c[0])
            shape1.append(c[1])
            i = 2
            while i < n:
                if math.fabs(c[i][0]-c[i-2][0]) > 0.001 or \
                        math.fabs(c[i][1]-c[i-2][1]) > 0.001:
                    shape1.append(c[i])
                else:
                    print "--> found zero width peninsula!!!"
                i += 1

            # look for 3 points in a row with the same x value
            shape2 = []
            shape2.append(shape1[0])
            i = 1
            while i < n - 1:
                if math.fabs(c[i-1][0]-c[i][0]) > 0.001 or \
                        math.fabs(c[i+1][0]-c[i][0]) > 0.001:
                    shape2.append(c[i])
                else:
                    print "--> found 3x in a row!!!"
                i += 1
            shape2.append(shape1[n-1])

            result.addContour(shape2)
        return result            

    # follow the inner contour of the rib on the top and bottom and
    # (hopefully) add rounded corners.  Right now left right walls are
    # vertical, but it should be possible to do angles (to leave an
    # interior triangle structure someday.)
    def carve_shaped_hole(self, pos1=None, pos2=None, \
                              material_width=0.0, radius=0.0):
        if self.poly == None:
            self.make_poly()

        bounds = self.get_bounds()

        # hollow entire interior (longitudinal axis) at cut radius +
        # corner radius.  This like the center 'cut' line if we were
        # cutting with a 'radius' radius tool.
        top = self.project_contour(surf="top", \
                                       xstart=bounds[0][0], \
                                       xend=bounds[1][0], \
                                       ysize=material_width+radius)
        bot = self.project_contour(surf="bottom", \
                                       xstart=bounds[0][0], \
                                       xend=bounds[1][0], \
                                       ysize=material_width+radius)
        top.reverse()
        shape = top + bot
        mask1 = Polygon.Polygon(shape)

        # vertical column (narrowed by radius)
        xstart = self.get_xpos( pos1 ) + radius
        xend = self.get_xpos( pos2 ) - radius
        shape = []
        shape.append( (xstart, bounds[0][1]) )
        shape.append( (xend, bounds[0][1]) )
        shape.append( (xend, bounds[1][1]) )
        shape.append( (xstart, bounds[1][1]) )
        mask2 = Polygon.Polygon(shape)

        # combined the shared area of the two hollowed shapes.
        # Essentially if we sweep a circle centered on the enge of
        # this polygon, the outer bounds of that cut is the final
        # shape we want
        mask_cut = mask1 & mask2

        # pretend we are cutting by placing a 'radius' size circle at
        # each point in the cut line and taking the union of all of
        # those (incrementally)
        mask = None
        for p in mask_cut[0]:
            circle = Polygon.Shapes.Circle(radius=radius, center=p, points=23)
            if mask == None:
                mask = circle
            else:
                mask = Polygon.Utils.convexHull(mask | circle)
                mask = self.reduce_degeneracy(mask)

        mask = Polygon.Utils.convexHull(mask)
        for p in mask:
            print "contour..."
            print p

        self.poly = self.poly - mask

                    
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

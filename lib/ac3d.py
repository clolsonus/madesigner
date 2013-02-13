#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy
import math


# maintain a list of unique vertices
class VertexDB:
    def __init__(self, tolerance=0.0001):
        self.v = []
        self.tolerance = tolerance

    # compare if a == b within tolerence
    def equal(self, a, b):
        if math.fabs(a[0]-b[0]) > self.tolerance or \
                math.fabs(a[1]-b[1]) > self.tolerance or \
                math.fabs(a[2]-b[2]) > self.tolerance:
        # (exact) if a[0] != b[0] or a[1] != b[1] or a[2] != b[2]:
            return False
        else:
            return True

    # add point and return the index slot of point
    def add_point(self, pt):
        size = len(self.v)
        i = size - 1
        # reverse search
        while i >= 0:
            if self.equal(self.v[i], pt):
                return i
            i -= 1
        self.v.append(pt)
        return size


class AC3D:
    def __init__(self, name=None):
        self.f = None
        if name:
            self.open(name)
    
    def open(self, name):
        self.name = name + ".ac"
        try:
            self.f = open( self.name, "w" )
        except IOError:
            print "Cannot open " + self.name

    def gen_headers(self, name, kids):
        self.f.write("AC3Db\n")
        self.f.write("MATERIAL \"res\" rgb 1 1 1 amb 1 1 1 emis 0 0 0 spec 0.2 0.2 0.2 shi 128 trans 0\n")
        self.f.write("OBJECT world\n")
        self.f.write("name \"" + name + "\"\n")
        self.f.write("kids " + str(kids) + "\n")

    def start_object_group(self, name, kids):
        self.f.write("OBJECT group\n")
        self.f.write("name \"" + name + "\"\n")
        self.f.write("kids " + str(kids) + "\n")

    def end_object_group(self):
        self.f.write("kids 0\n")

    def make_object_poly(self, name, poly2d, thickness, pos, nudge):
        halfw = thickness*0.5
        surfs = 0
        vertices = VertexDB()

        # pass 1a assemble unique vertex list and count outer edge surfs
        for contour in poly2d:
            surfs += len(contour)
            for p2 in contour:
                p3 = (p2[0], -halfw-nudge, p2[1])
                v = vertices.add_point(p3)
                p3 = (p2[0], +halfw-nudge, p2[1])
                v = vertices.add_point(p3)

        # pass 1b run through the tristrip and count the number of
        # side face tris
        strip_list = poly2d.triStrip()
        for strip in strip_list:
            # times 2 because we have 2 sides
            surfs += 2 * (len(strip) - 2)
            for p2 in strip:
                p3 = (p2[0], -halfw-nudge, p2[1])
                v = vertices.add_point(p3)
                p3 = (p2[0], +halfw-nudge, p2[1])
                v = vertices.add_point(p3)

        print "vertex db = " + str(len(vertices.v))
        self.f.write("OBJECT poly\n")
        self.f.write("name \"" + name + "\"\n")
        self.f.write("loc " + str(pos[1]) + " " + str(pos[0]) + " " + str(pos[2]) + "\n")
        self.f.write("numvert " + str(len(vertices.v)) + "\n")
        for v in vertices.v:
            self.f.write(str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + "\n")

        # pass 2, make side triangles
        self.f.write("numsurf " + str(surfs) + "\n")
        # side 1
        for strip in strip_list:
            v1 = 0
            v2 = 0
            flip = True
            for i, p2 in enumerate(strip):
                p3 = (p2[0], -halfw-nudge, p2[1])
                v = vertices.add_point(p3)
                if i > 1:
                    self.f.write("SURF 0x10\n")
                    self.f.write("mat 0\n")
                    self.f.write("refs 3\n")
                    if flip:
                        self.f.write(str(v) + " 0 0\n")
                        self.f.write(str(v2) + " 0 0\n")
                        self.f.write(str(v1) + " 0 0\n")
                    else:
                        self.f.write(str(v) + " 0 0\n")
                        self.f.write(str(v1) + " 0 0\n")
                        self.f.write(str(v2) + " 0 0\n")
                    flip = not flip
                v2 = v1
                v1 = v
        # side 2
        for strip in strip_list:
            v1 = 0
            v2 = 0
            flip = False
            for i, p2 in enumerate(strip):
                p3 = (p2[0], halfw-nudge, p2[1])
                v = vertices.add_point(p3)
                if i > 1:
                    self.f.write("SURF 0x10\n")
                    self.f.write("mat 0\n")
                    self.f.write("refs 3\n")
                    if flip:
                        self.f.write(str(v) + " 0 0\n")
                        self.f.write(str(v2) + " 0 0\n")
                        self.f.write(str(v1) + " 0 0\n")
                    else:
                        self.f.write(str(v) + " 0 0\n")
                        self.f.write(str(v1) + " 0 0\n")
                        self.f.write(str(v2) + " 0 0\n")
                    flip = not flip
                v2 = v1
                v1 = v

        # pass 3 make edge triangles
        for contour in poly2d:
            for i, p2 in enumerate(contour):
                p3a = (p2[0], -halfw-nudge, p2[1])
                p3b = (p2[0], halfw-nudge, p2[1])
                v1a = vertices.add_point(p3a)
                v1b = vertices.add_point(p3b)
                if i > 0:
                    self.f.write("SURF 0x10\n")
                    self.f.write("mat 0\n")
                    self.f.write("refs 4\n")
                    self.f.write(str(v0a) + " 0 0\n")
                    self.f.write(str(v1a) + " 0 0\n")
                    self.f.write(str(v1b) + " 0 0\n")
                    self.f.write(str(v0b) + " 0 0\n")
                v0a = v1a
                v0b = v1b
            # connect the loop to the front
            p3a = (contour[0][0], -halfw-nudge, contour[0][1])
            p3b = (contour[0][0], halfw-nudge, contour[0][1])
            v1a = vertices.add_point(p3a)
            v1b = vertices.add_point(p3b)
            self.f.write("SURF 0x10\n")
            self.f.write("mat 0\n")
            self.f.write("refs 4\n")
            self.f.write(str(v0a) + " 0 0\n")
            self.f.write(str(v1a) + " 0 0\n")
            self.f.write(str(v1b) + " 0 0\n")
            self.f.write(str(v0b) + " 0 0\n")

        self.f.write("kids 0\n")

    def make_extrusion(self, name, points, invert_order):
        surfs = 0
        vertices = VertexDB()

        # pass 1 assemble unique vertex list and count outer edge surfs
        i = 0
        while i < len(points):
            contour = points[i]
            if i > 0:
                surfs += len(contour)
            for p3 in contour:
                v = vertices.add_point(p3)
            i += 1

        # account for the end faces of the extrusion
        surfs += 2

        print "vertex db = " + str(len(vertices.v))
        self.f.write("OBJECT poly\n")
        self.f.write("name \"" + name + "\"\n")
        self.f.write("loc 0 0 0\n")
        self.f.write("numvert " + str(len(vertices.v)) + "\n")
        for v in vertices.v:
            self.f.write(str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + "\n")

        self.f.write("numsurf " + str(surfs) + "\n")
        print "predict numsurf = " + str(surfs)

        # pass 2, make side triangles
        tmp = 0
        i = 1
        while i < len(points):
            c0 = points[i-1]
            c1 = points[i]
            j = 0
            while j < len(c0) and j < len(c1):
                p0 = c0[j]
                p1 = c0[(j+1) % len(c0)]
                p2 = c1[j]
                p3 = c1[(j+1) % len(c1)]
                v0 = vertices.add_point(p0)
                v1 = vertices.add_point(p1)
                v2 = vertices.add_point(p2)
                v3 = vertices.add_point(p3)

                self.f.write("SURF 0x10\n")
                self.f.write("mat 0\n")
                self.f.write("refs 4\n")
                if not invert_order:
                    self.f.write(str(v0) + " 0 0\n")
                    self.f.write(str(v2) + " 0 0\n")
                    self.f.write(str(v3) + " 0 0\n")
                    self.f.write(str(v1) + " 0 0\n")
                else:
                    self.f.write(str(v0) + " 0 0\n")
                    self.f.write(str(v1) + " 0 0\n")
                    self.f.write(str(v3) + " 0 0\n")
                    self.f.write(str(v2) + " 0 0\n")
                tmp += 1
                j += 1
            i += 1

        # make the two end caps
        self.f.write("SURF 0x10\n")
        self.f.write("mat 0\n")
        pts = list(copy.deepcopy(points[0]))
        if invert_order:
            pts.reverse()
        n = len(pts)
        self.f.write("refs " + str(n) + "\n")
        i = 0
        while i < n:
            p = pts[i]
            v = vertices.add_point(p)
            self.f.write(str(v) + " 0 0\n")
            i += 1
  
        self.f.write("SURF 0x10\n")
        self.f.write("mat 0\n")
        pts = list(copy.deepcopy(points[len(points)-1]))
        if not invert_order:
            pts.reverse()
        n = len(pts)
        self.f.write("refs " + str(n) + "\n")
        i = 0
        while i < n:
            p = pts[i]
            v = vertices.add_point(p)
            self.f.write(str(v) + " 0 0\n")
            i += 1

        print "actual surf = " + str(tmp)
        self.f.write("kids 0\n")

    def close(self):
        self.f.write("kids 0\n")
        self.f.close()

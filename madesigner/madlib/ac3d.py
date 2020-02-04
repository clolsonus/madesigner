
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
            print("Cannot open " + self.name)

    def gen_headers(self, name, kids):
        self.f.write("AC3Db\n")
        self.f.write("MATERIAL \"res\" rgb 1 1 1 amb 1 1 1 emis 0 0 0 spec 0.2 0.2 0.2 shi 128 trans 0\n")
        self.f.write("MATERIAL \"res\" rgb 1 1 1 amb 1 1 1 emis 0 0 0 spec 0.2 0.2 0.2 shi 128 trans 0.25\n")
        self.f.write("OBJECT world\n")
        self.f.write("name \"" + name + "\"\n")
        self.f.write("kids " + str(kids) + "\n")

    def start_object_group(self, name, kids, m=None, loc=None):
        self.f.write("OBJECT group\n")
        self.f.write("name \"" + name + "\"\n")
        if loc:
            self.f.write("loc ")
            for v in loc:
                self.f.write(str(v) + " ")
            self.f.write("\n")
        if m:
            self.f.write("rot ")
            for row in m:
                for v in row:
                    self.f.write(str(v) + " ")
            self.f.write("\n")
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

        print("vertex db = " + str(len(vertices.v)))
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

    def myint(self, x ):
        if x > 0:
            return int(x + 0.5)
        else:
            return int(x - 0.5)

    def make_sheet_help1(self, vertices, top_points, invert_order):
        # make surface polys
        tmp = 0
        i = 1
        #print "help1 *new* " + str(len(top_points)) + " " + str(top_points)
        while i < len(top_points):
            c0 = top_points[i-1]
            c1 = top_points[i]
            len_c0 = len(c0) - 1
            len_c1 = len(c1) - 1
            ratio = float(len_c0) / float(len_c1)
            #print "len(c0)-1=" + str(len_c0) + " len(c1)-1=" + str(len_c1)
            #print "ratio=" + str(ratio)
            j_inc = 1.0
            k_inc = 1.0
            if ratio > 1.0:
                k_inc = 1.0 / ratio
            elif ratio < 1.0:
                j_inc = ratio
            j_real = j_inc
            k_real = k_inc
            j = self.myint(j_real)
            k = self.myint(k_real)
            j_prev = 0
            k_prev = 0
            while j <= len_c0 and k <= len_c1:
                #print "i=" + str(i) + " j=" + str(j) + " k=" + str(k)
                p0 = c0[j_prev]
                if j > j_prev:
                    p1 = c0[j]
                else:
                    p1 = None
                p2 = c1[k_prev]
                if k > k_prev:
                    p3 = c1[k]
                else:
                    p3 = None
                vlist = []
                if p3 == None:
                    vlist.append( vertices.add_point(p0) )
                    vlist.append( vertices.add_point(p1) )
                    vlist.append( vertices.add_point(p2) )
                elif p1 == None:
                    vlist.append( vertices.add_point(p0) )
                    vlist.append( vertices.add_point(p3) )
                    vlist.append( vertices.add_point(p2) )
                else:
                    vlist.append( vertices.add_point(p0) )
                    vlist.append( vertices.add_point(p1) )
                    vlist.append( vertices.add_point(p3) )
                    vlist.append( vertices.add_point(p2) )
                j_prev = j
                k_prev = k
                j_real += j_inc
                k_real += k_inc
                j = self.myint(j_real)
                k = self.myint(k_real)
                self.f.write("SURF 0x10\n")
                self.f.write("mat 1\n")
                self.f.write("refs " + str(len(vlist)) + "\n")
                if invert_order:
                    vlist.reverse()
                for v in vlist:
                    self.f.write(str(v) + " 0 0\n")
                tmp += 1
            i += 1
        return tmp

    def make_sheet_help2(self, vertices, top_points, bot_points, invert_order):
        # make edge (lengthwise) polys
        if len(top_points) != len(bot_points):
            print("top/bottom surface size mismatch in making sheets!")
            return 0

        tmp = 0
        i = 1
        while i < len(top_points):
            c0 = top_points[i-1]
            c1 = top_points[i]
            c2 = bot_points[i-1]
            c3 = bot_points[i]

            # edge 1
            vlist = []
            p0 = c0[0]
            p1 = c1[0]
            p2 = c2[0]
            p3 = c3[0]
            vlist.append( vertices.add_point(p0) )
            vlist.append( vertices.add_point(p1) )
            vlist.append( vertices.add_point(p3) )
            vlist.append( vertices.add_point(p2) )
            self.f.write("SURF 0x10\n")
            self.f.write("mat 1\n")
            self.f.write("refs " + str(len(vlist)) + "\n")
            if invert_order:
                vlist.reverse()
            for v in vlist:
                self.f.write(str(v) + " 0 0\n")

            # edge 2
            vlist = []
            p0 = c0[len(c0)-1]
            p1 = c1[len(c1)-1]
            p2 = c2[len(c2)-1]
            p3 = c3[len(c3)-1]
            vlist.append( vertices.add_point(p0) )
            vlist.append( vertices.add_point(p2) )
            vlist.append( vertices.add_point(p3) )
            vlist.append( vertices.add_point(p1) )
            self.f.write("SURF 0x10\n")
            self.f.write("mat 1\n")
            self.f.write("refs " + str(len(vlist)) + "\n")
            if invert_order:
                vlist.reverse()
            for v in vlist:
                self.f.write(str(v) + " 0 0\n")

            i += 1
            tmp += 2
        return tmp

    def make_sheet_help3(self, vertices, top_points, bot_points, invert_order):
        # make end polys
        tmp = 0

        # end 1
        c0 = top_points[0]
        c1 = bot_points[0]
        i = 1
        while i < len(c0):
            p0 = c0[i-1]
            p1 = c0[i]
            p2 = c1[i-1]
            p3 = c1[i]
            vlist = []
            vlist.append( vertices.add_point(p0) )
            vlist.append( vertices.add_point(p2) )
            vlist.append( vertices.add_point(p3) )
            vlist.append( vertices.add_point(p1) )
            self.f.write("SURF 0x10\n")
            self.f.write("mat 1\n")
            self.f.write("refs " + str(len(vlist)) + "\n")
            if invert_order:
                vlist.reverse()
            for v in vlist:
                self.f.write(str(v) + " 0 0\n")
            tmp += 1
            i += 1
        
        # end 2
        c0 = top_points[len(top_points)-1]
        c1 = bot_points[len(bot_points)-1]
        i = 1
        while i < len(c0):
            p0 = c0[i-1]
            p1 = c0[i]
            p2 = c1[i-1]
            p3 = c1[i]
            vlist = []
            vlist.append( vertices.add_point(p0) )
            vlist.append( vertices.add_point(p1) )
            vlist.append( vertices.add_point(p3) )
            vlist.append( vertices.add_point(p2) )
            self.f.write("SURF 0x10\n")
            self.f.write("mat 1\n")
            self.f.write("refs " + str(len(vlist)) + "\n")
            if invert_order:
                vlist.reverse()
            for v in vlist:
                self.f.write(str(v) + " 0 0\n")
            tmp += 1
            i += 1
        return tmp

    def make_sheet(self, name, top_points, bot_points, invert_order):
        surfs = 0
        vertices = VertexDB()

        print("make sheet")
        print("top points = " + str(len(top_points)))
        print("bottom points = " + str(len(bot_points)))

        # pass 1 assemble unique vertex list and count surfs
        i = 0
        while i < len(top_points):
            contour = top_points[i]
            if i > 0:
                last_contour = top_points[i-1]
                last_len = len(last_contour)
                cur_len = len(contour)
                if last_len > cur_len:
                    surfs += last_len
                else:
                    surfs += cur_len
            for p3 in contour:
                v = vertices.add_point(p3)
            i += 1
        i = 0
        while i < len(bot_points):
            contour = bot_points[i]
            if i > 0:
                last_contour = bot_points[i-1]
                last_len = len(last_contour)
                cur_len = len(contour)
                if last_len > cur_len:
                    surfs += last_len
                else:
                    surfs += cur_len
            for p3 in contour:
                v = vertices.add_point(p3)
            i += 1

        # account for the end faces of the extrusion
        surfs += len(top_points[0]) - 1
        surfs += len(top_points[len(top_points)-1]) - 1

        print("vertex db = " + str(len(vertices.v)))
        self.f.write("OBJECT poly\n")
        self.f.write("name \"" + name + "\"\n")
        self.f.write("loc 0 0 0\n")
        self.f.write("numvert " + str(len(vertices.v)) + "\n")
        for v in vertices.v:
            self.f.write(str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + "\n")

        self.f.write("numsurf " + str(surfs) + "\n")
        print("predict numsurf(sheet) = " + str(surfs))

        # pass 2, make top surface triangles
        total = 0
        total += self.make_sheet_help1(vertices, top_points, invert_order)
        total += self.make_sheet_help1(vertices, bot_points, not invert_order)
        total += self.make_sheet_help2(vertices, top_points, bot_points, invert_order)
        total += self.make_sheet_help3(vertices, top_points, bot_points, invert_order)

        print("actual surf = " + str(total))
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

        #print "vertex db = " + str(len(vertices.v))
        self.f.write("OBJECT poly\n")
        self.f.write("name \"" + name + "\"\n")
        self.f.write("loc 0 0 0\n")
        self.f.write("numvert " + str(len(vertices.v)) + "\n")
        for v in vertices.v:
            self.f.write(str(v[0]) + " " + str(v[1]) + " " + str(v[2]) + "\n")

        self.f.write("numsurf " + str(surfs) + "\n")
        #print "predict numsurf = " + str(surfs)

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

        print("actual surf = " + str(tmp))
        self.f.write("kids 0\n")

    def close(self):
        self.f.write("kids 0\n")
        self.f.close()

    def make_rotation_matrix(self, axis, angle):
        m = None
        rad = math.radians(angle)
        sa = math.sin(rad)
        ca = math.cos(rad)
        if axis == "x" or axis == "X":
            m = ( (1.0, 0.0, 0.0),
                  (0.0, ca, -sa),
                  (0.0, sa,  ca) )
        elif axis == "y" or axis == "Y":
            m = ( (ca,  0.0, -sa),
                  (0.0, 1.0, 0.0),
                  (sa,  0.0,  ca) )
        elif axis == "z" or axis == "Z":
            m = ( (ca,  -sa,  0.0),
                  (sa,   ca,  0.0),
                  (0.0, 0.0,  1.0) )

        return m

    def multiply_rotation_matrix(self, A, B):
        m = [ [0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0] ]
        print(str(m[1][1]))
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    m[i][j] += A[i][k] * B[k][j]
        return m

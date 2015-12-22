#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy
import numpy as np
import Polygon
import Polygon.IO
import Polygon.Utils
import svgwrite

import airfoil


class Sheet:

    def __init__(self, name, width, height, step=None, units="in", dpi=90):
        self.dwg = svgwrite.Drawing( name + '.svg', size = (str(width)+units, str(height)+units) )
        self.width = width
        self.height = height
        if step != None:
            self.step = step
        else:
            self.step = 0.1
        self.units = units
        self.dpi = dpi
        if units == "mm":
            self.dpi = self.dpi / 25.4
        elif units == "cm":
            self.dpi = self.dpi / 2.54
        self.dwg.viewbox( 0, 0, self.width*self.dpi, self.height*self.dpi )
        #self.ypos = 0.0 + self.step
        self.xpos = 0.0 + self.step
        #self.biggest_x = 0.0
        self.mask = Polygon.Polygon()

    def draw_part_side(self, part, stroke_width="1px", color="red",
                       lines=True, points=False, outline=False, speed="fast"):
        print "Placing:", part.labels
        if part.poly == None:
            part.make_poly()
        p = copy.deepcopy(part.poly)
        p.flop(0.0)
        bounds = p.boundingBox()
        dx = bounds[1] - bounds[0]
        dy = bounds[3] - bounds[2]
        print "dx:", dx, "dy:", dy

        # make layout sheet polygon
        sheet = Polygon.Polygon([ [0, 0],
                                  [self.width, 0],
                                  [self.width, self.height],
                                  [0, self.height] ])
        
        if speed == "fast":
            hull = Polygon.Polygon( [ [bounds[0], bounds[2]],
                                      [bounds[1], bounds[2]],
                                      [bounds[1], bounds[3]],
                                      [bounds[0], bounds[3]] ])
        elif speed == "medium":
            # make convex hull outline of polygon, and make grow it a tiny bit
            hull = Polygon.Utils.convexHull(p)
        elif speed == "nice":
            # more details polygon yields better fit, but nesting takes longer
            hull = Polygon.Utils.fillHoles(p)
        else:
            print "ERROR: Unknown nesting speed/quality:", speed
            print "Defaulting to 'fast'"
            hull = Polygon.Polygon( [ [bounds[0], bounds[2]],
                                      [bounds[1], bounds[2]],
                                      [bounds[1], bounds[3]],
                                      [bounds[0], bounds[3]] ])

        hull.scale((dx+self.step)/dx, (dy+self.step)/dy)
        hull180 = Polygon.Polygon(hull)
        hull180.rotate(180.0)
        
        # nest the hull against the existing sheet mask
        x = 0.0
        found = False
        while not found and x + dx + self.step < self.width:
            x += self.step
            y = 0.0
            while not found and y + dy + self.step < self.height:
                y += self.step
                bmask = Polygon.Polygon(hull)
                bmask.shift(x, y)
                if sheet.covers(bmask) and not self.mask.overlaps(bmask):
                    found = True

        if not found:
            return False

        # merge bounds mask into sheet mask
        self.mask += bmask

        #Polygon.IO.writeGnuplotTriangles("mask.plt", [self.mask])
        #result = raw_input("press enter to continue:")
        
        g = self.dwg.g()
        #g.translate((x-bounds[0])*self.dpi,
        #            (y-bounds[2])*self.dpi)
        g.translate((x)*self.dpi,
                    (y)*self.dpi)

        p.scale( self.dpi, self.dpi, 0.0, 0.0 )

        if outline:
            tmp = copy.deepcopy(part)
            tmp.scale( self.dpi, -self.dpi )
            shape = tmp.top
            shape.reverse()
            shape += tmp.bottom
            poly = self.dwg.polygon(shape, stroke='blue', fill='none',
                                    stroke_width=stroke_width)
            g.add( poly )

        if lines:
            for shape in p:
                poly = self.dwg.polygon(shape, stroke='red', fill='none',
                                        stroke_width=stroke_width)
                g.add( poly )
            if len(part.cut_lines):
                shape = np.array(part.cut_lines)
                print "shape:", shape
                shape[:,2] *= -1.0  # invert vertical axis
                shape *= self.dpi   # scale for drawing
                for i in range(len(part.cut_lines) / 2):
                    p1 = shape[2*i]
                    p2 = shape[2*i + 1]
                    print "line:", p1, p2
                    line = self.dwg.line([p1[0], p1[2]], [p2[0], p2[2]],
                                         stroke='red', fill='none',
                                         stroke_width=stroke_width)
                    g.add( line )

        for label in part.labels:
            #print "label = " + str(label[0]) + "," + str(label[1])
            t = self.dwg.text(label[4], (0, 0), font_size=label[2],
                              text_anchor="middle", stroke='blue', fill='none',
                              stroke_width=stroke_width)
            t.translate( (label[0]*self.dpi, -label[1]*self.dpi) )
            t.rotate(-label[3])
            # text_align = center
            g.add(t)

        if points:
            for shape in p:
                for pt in shape:
                    c = self.dwg.circle( center=pt, r=2, stroke='green',
                                         fill='green', opacity=0.6 )
                    g.add(c)

        self.dwg.add(g)

        return True

    def draw_part_top(self, offset, orig_contour, pos, part_width, nudge, \
                          stroke_width, color ):
        # sanity check
        if orig_contour.poly == None:
            orig_contour.make_poly()
        contour = copy.deepcopy(orig_contour)
        #contour.scale(1,-1)
        bounds = contour.poly.boundingBox()
        dx = bounds[1] - bounds[0]
        #print "contour bounds = " + str(bounds)
        #print "dx = " + str(dx)

        contour.scale( self.dpi, self.dpi )
        shape = []
        x1 = bounds[0] * self.dpi
        x2 = bounds[1] * self.dpi
        y1 = -part_width*0.5 * self.dpi
        y2 = part_width*0.5 * self.dpi

        #print (bounds[0], bounds[1])
        #print pos[1]
        #print (y1, y2)
        shape.append( (x1, y1) )
        shape.append( (x2, y1) )
        shape.append( (x2, y2) )
        shape.append( (x1, y2) )
        #print "draw_rib = " + str(shape)
        g = self.dwg.g()
        #print " at offset = " + str(offset)
        g.translate( (pos[1] + offset[0])*self.dpi, \
                         (-pos[0] + offset[1] + nudge)*self.dpi )

        poly = self.dwg.polygon(shape, stroke = 'red', fill = 'none', \
                                    stroke_width = stroke_width)
        g.add( poly )

        for label in contour.labels:
            yoffset = -part_width
            if nudge > 0.001:
                yoffset = 2.5*part_width + nudge
            #print "label = " + str(label[0]) + "," + str(label[1])
            t = self.dwg.text(label[4], (0, 0), font_size = label[2], text_anchor = "middle")
            t.translate( ((bounds[0] + dx*0.5)*self.dpi, \
                              yoffset*self.dpi) )
            # text_align = center
            g.add(t)

        self.dwg.add(g)

        return True

    def draw_shape(self, offset, shape, stroke_width, color ):
        g = self.dwg.g()
        #print " at offset = " + str(offset)
        g.translate( offset[0]*self.dpi, offset[1]*self.dpi )

        scaled = []
        for pt in shape:
            scaled.append( (pt[0]*self.dpi, pt[1]*self.dpi) )

        poly = self.dwg.polygon(scaled, stroke = 'red', fill = 'none', \
                                    stroke_width = stroke_width)
        g.add( poly )

        self.dwg.add(g)

        return True

    def save(self):
        self.dwg.save()


class Layout:

    def __init__(self, basename, width, height, step=None, units="in", dpi=90):
        self.basename = basename
        self.width = width
        self.height = height
        self.units = units
        if step != None:
            self.step = step
        else:
            if units == "in":
                self.step = 0.1
            elif units == "mm":
                self.step = 3
            elif units == "cm":
                self.step = 0.3
            else:
                self.step = 0.1
        self.dpi = dpi
        self.sheets = []

    def draw_part(self, part, stroke_width="1px", color="red", lines=False,
                  points=False, outline=False, speed="fast" ):
        # sanity check that part will fit on a sheet
        bounds = part.get_bounds()
        dx = bounds[1][0] - bounds[0][0]
        dy = bounds[1][1] - bounds[0][1]
        if (dx > self.width - 2*self.step) or \
                (dy > self.height - 2*self.step):
            if len(part.labels):
                print "Failed to fit: " + part.labels[0][4]
            else:
                print "Failed to fit: " + part.name
            print "  Part (" + str(dx) + "x" + str(dy) + self.units \
                + ") exceed size of sheet (" + str(self.width) + "x" \
                + str(self.height) + self.units +")"
            return False
        num_sheets = len(self.sheets)
        i = 0
        done = False
        while i < num_sheets and not done:
            done = self.sheets[i].draw_part_side(part, stroke_width, color,
                                                 lines, points, outline, speed)
            i += 1
        if not done:
            # couldn't fit on any existing sheet so create a new one
            sheet = Sheet(self.basename + str(i), self.width, self.height,
                          step=self.step, units=self.units, dpi=self.dpi)
            done = sheet.draw_part_side(part, stroke_width, color, lines,
                                        points, outline, speed)
            self.sheets.append(sheet)
        if not done:
            print "this should never happen!"
            if len(part.labels):
                print "Failed to fit: " + part.labels[0][4]
            else:
                print "Failed to fit: " + part.name
        return done

    def draw_part_cut_line(self, airfoil, speed):
        self.draw_part(airfoil, stroke_width="0.001in", color="red", lines=True,
                       speed=speed)

    def draw_part_plan_side(self, airfoil, speed):
        self.draw_part(airfoil, stroke_width="1px", color="red", lines=True,
                       speed=speed)

    def draw_part_demo(self, airfoil, speed):
        self.draw_part(airfoil, stroke_width="1px", color="red", lines=True,
                       points=True, outline=True, speed=speed)

    def draw_part_vertices(self, airfoil, speed):
        self.draw_part(airfoil, stroke_width="1px", color="red", points=True,
                       speed=speed)

    def save(self):
        for sheet in self.sheets:
            sheet.save()

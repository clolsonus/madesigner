#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy
import svgwrite
import airfoil


class Sheet:

    def __init__(self, name, width, height, margin = 0.1, units = "in", dpi = 90):
        self.dwg = svgwrite.Drawing( name + '.svg', size = (str(width)+units, str(height)+units) )
        self.dwg.viewbox( 0, 0, width*dpi, height*dpi )
        self.width = width
        self.height = height
        self.margin = margin
        self.units = units
        self.dpi = dpi
        self.ypos = 0.0 + self.margin
        self.xpos = 0.0 + self.margin
        self.biggest_x = 0.0

    def draw_part_side(self, part, stroke_width="1px", color="red", \
                           lines=True, points=False, outline=False):
        if part.poly == None:
            part.make_poly()
        p = copy.deepcopy(part.poly)
        p.flop(0.0)
        bounds = p.boundingBox()
        dx = bounds[1] - bounds[0]
        dy = bounds[3] - bounds[2]

        p.scale( self.dpi, self.dpi, 0.0, 0.0 )
        if self.ypos + dy + self.margin > self.height:
            self.xpos += self.biggest_x + self.margin
            self.ypos = self.margin
            self.biggest_x = 0.0
        if self.xpos + dx + self.margin > self.width:
            return False

        g = self.dwg.g()
        g.translate((self.xpos-bounds[0])*self.dpi, \
                        (self.ypos-bounds[2])*self.dpi)
        self.ypos += dy + self.margin
        if dx > self.biggest_x:
            self.biggest_x = dx

        if outline:
            tmp = copy.deepcopy(part)
            tmp.scale( self.dpi, -self.dpi )
            shape = tmp.top
            shape.reverse()
            shape += tmp.bottom
            poly = self.dwg.polygon(shape, stroke='blue', fill='none', \
                                        stroke_width=stroke_width)
            g.add( poly )

        if lines:
            for shape in p:
                poly = self.dwg.polygon(shape, stroke = 'red', fill = 'none', \
                                            stroke_width = stroke_width)
                g.add( poly )

        for label in part.labels:
            #print "label = " + str(label[0]) + "," + str(label[1])
            t = self.dwg.text(label[4], (0, 0), font_size = label[2], text_anchor = "middle")
            t.translate( (label[0]*self.dpi, -label[1]*self.dpi) )
            t.rotate(-label[3])
            # text_align = center
            g.add(t)

        if points:
            for shape in p:
                for pt in shape:
                    c = self.dwg.circle( center = pt, r = 2, stroke = 'green', \
                                             fill = 'green', opacity = 0.6)
                    g.add(c)

        self.dwg.add(g)

        return True

    def draw_part_top(self, offset, orig_airfoil, pos, part_width, nudge, \
                          stroke_width, color ):
        airfoil = copy.deepcopy(orig_airfoil)
        airfoil.scale(1,-1)
        bounds = airfoil.get_bounds()
        dx = bounds[1][0] - bounds[0][0]

        airfoil.scale( self.dpi, self.dpi )
        shape = []
        x1 = bounds[0][0] * self.dpi
        x2 = bounds[1][0] * self.dpi
        y1 = -part_width*0.5 * self.dpi
        y2 = part_width*0.5 * self.dpi

        #print (bounds[0][0], bounds[1][0])
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

        for label in airfoil.labels:
            yoffset = -part_width
            if nudge > 0.001:
                yoffset = 2.5*part_width + nudge
            #print "label = " + str(label[0]) + "," + str(label[1])
            t = self.dwg.text(label[4], (0, 0), font_size = label[2], text_anchor = "middle")
            t.translate( ((bounds[0][0] + dx*0.5)*self.dpi, \
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

    def __init__(self, basename, width, height, margin = 0.1, units = "in", dpi = 90):
        self.basename = basename
        self.width = width
        self.height = height
        self.margin = margin
        self.units = units
        self.dpi = dpi
        self.sheets = []

    def draw_part(self, part, stroke_width="1px", color="red", \
                      lines=False, points=False, outline=False ):
        # sanity check that part will fit on a sheet
        bounds = part.get_bounds()
        dx = bounds[1][0] - bounds[0][0]
        dy = bounds[1][1] - bounds[0][1]
        if (dx > self.width - 2*self.margin) or \
                (dy > self.height - 2*self.margin):
            if len(part.labels):
                print "Failed to fit: " + part.labels[0][4]
            else:
                print "Failed to fit: " + part.name
            print "- Part dimensions exceed size of sheet!"
            return False
        num_sheets = len(self.sheets)
        i = 0
        done = False
        while i < num_sheets and not done:
            done = self.sheets[i].draw_part_side(part, stroke_width, color, \
                                                     lines, points, outline)
            i += 1
        if not done:
            # couldn't fit on any existing sheet so create a new one
            sheet = Sheet(self.basename + str(i), self.width, \
                              self.height, self.margin, self.units, self.dpi)
            done = sheet.draw_part_side(part, stroke_width, color, lines, \
                                            points, outline)
            self.sheets.append(sheet)
        if not done:
            print "this should never happen!"
            if len(part.labels):
                print "Failed to fit: " + part.labels[0][4]
            else:
                print "Failed to fit: " + part.name
        return done

    def draw_part_cut_line(self, airfoil ):
        self.draw_part(airfoil, stroke_width="0.001in", color="red", lines=True)

    def draw_part_plan_side(self, airfoil ):
        self.draw_part(airfoil, stroke_width="1px", color="red", lines=True)

    def draw_part_demo(self, airfoil ):
        self.draw_part(airfoil, stroke_width="1px", color="red", \
                           lines=True, points=True, outline=True )

    def draw_part_vertices(self, airfoil ):
        self.draw_part(airfoil, stroke_width="1px", color="red", points=True)

    def save(self):
        for sheet in self.sheets:
            sheet.save()

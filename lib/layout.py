#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy

import svgwrite

import airfoil


class Sheet:

    def __init__(self, name, width_in, height_in, margin_in = 0.1, dpi = 90):
        self.dwg = svgwrite.Drawing( name + '.svg', size = ( '{:.2f}in'.format(width_in), '{:.2f}in'.format(height_in) ) )
        self.dwg.viewbox( 0, 0, width_in*dpi, height_in*dpi )
        self.width_in = width_in
        self.height_in = height_in
        self.margin = margin_in
        self.dpi = dpi
        self.ypos = 0.0 + self.margin
        self.xpos = 0.0 + self.margin
        self.biggest_x = 0.0

    def draw_part_side(self, orig_airfoil, stroke_width, color, \
                           lines = True, points = False ):
        airfoil = copy.deepcopy(orig_airfoil)
        airfoil.scale(1,-1)
        bounds = airfoil.get_bounds()
        dx = bounds[1][0] - bounds[0][0]
        dy = bounds[1][1] - bounds[0][1]

        airfoil.scale( self.dpi, self.dpi )
        reverse_top = list(airfoil.top)
        reverse_top.reverse()
        shape = reverse_top + airfoil.bottom
        if self.ypos + dy + self.margin > self.height_in:
            self.xpos += self.biggest_x + self.margin
            self.ypos = self.margin
            self.biggest_x = 0.0
        if self.xpos + dx + self.margin > self.width_in:
            return False
        g = self.dwg.g()
        g.translate((self.xpos-bounds[0][0])*self.dpi, \
                        (self.ypos-bounds[0][1])*self.dpi)
        self.ypos += dy + self.margin
        if dx > self.biggest_x:
            self.biggest_x = dx

        if lines:
            poly = self.dwg.polygon(shape, stroke = 'red', fill = 'none', \
                                        stroke_width = stroke_width)
            g.add( poly )

        for hole in airfoil.holes:
            pt = ( hole[0], hole[1] )
            radius = hole[2]
            c = self.dwg.circle( center = pt, r = radius, stroke = 'red', \
                                     fill = 'none', \
                                     stroke_width = stroke_width)
            g.add(c)

        for label in airfoil.labels:
            #print "label = " + str(label[0]) + "," + str(label[1])
            t = self.dwg.text(label[4], (0, 0), font_size = label[2], text_anchor = "middle")
            t.translate( (label[0], label[1]) )
            t.rotate(-label[3])
            # text_align = center
            g.add(t)

        if points:
            for pt in shape:
                c = self.dwg.circle( center = pt, r = 2, stroke = 'green', \
                                    fill = 'green', opacity = 0.6)
                g.add(c)

        self.dwg.add(g)

        return True

    def draw_part_top(self, offset, orig_airfoil, pos, stroke_width, color ):
        airfoil = copy.deepcopy(orig_airfoil)
        airfoil.scale(1,-1)
        bounds = airfoil.get_bounds()
        dx = bounds[1][0] - bounds[0][0]

        airfoil.scale( self.dpi, self.dpi )
        shape = []
        part_width = 0.125
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
                         (-pos[0] + offset[1])*self.dpi )

        poly = self.dwg.polygon(shape, stroke = 'red', fill = 'none', \
                                    stroke_width = stroke_width)
        g.add( poly )

        for label in airfoil.labels:
            #print "label = " + str(label[0]) + "," + str(label[1])
            t = self.dwg.text(label[4], (0, 0), font_size = label[2], text_anchor = "middle")
            t.translate( ((bounds[0][0] + dx*0.5)*self.dpi, \
                              -part_width*self.dpi) )
            # text_align = center
            g.add(t)

        self.dwg.add(g)

        return True

    def save(self):
        self.dwg.save()


class Layout:

    def __init__(self, basename, width_in, height_in, margin_in = 0.1, dpi = 90):
        self.basename = basename
        self.width_in = width_in
        self.height_in = height_in
        self.margin_in = margin_in
        self.dpi = dpi
        self.sheets = []

    def draw_part(self, af, stroke_width, color, lines = True, points = False ):
        # sanity check that part will fit on a sheet
        bounds = af.get_bounds()
        dx = bounds[1][0] - bounds[0][0]
        dy = bounds[1][1] - bounds[0][1]
        if (dx > self.width_in - 2*self.margin_in) or \
                (dy > self.height_in - 2*self.margin_in):
            if len(af.labels):
                print "Failed to fit: " + af.labels[0][4]
            else:
                print "Failed to fit: " + af.name
            print "- Part dimensions exceed size of sheet!"
            return False
        num_sheets = len(self.sheets)
        i = 0
        done = False
        while i < num_sheets and not done:
            done = self.sheets[i].draw_part_side(af, stroke_width, color, \
                                                     lines, points)
            i += 1
        if not done:
            # couldn't fit on any existing sheet so create a new one
            sheet = Sheet(self.basename + str(i), self.width_in, \
                              self.height_in, self.margin_in, self.dpi)
            done = sheet.draw_part_side(af, stroke_width, color, lines, points)
            self.sheets.append(sheet)
        if not done:
            print "this should never happen!"
            if len(af.labels):
                print "Failed to fit: " + af.labels[0][4]
            else:
                print "Failed to fit: " + af.name
        return done

    def draw_part_cut_line(self, airfoil ):
        self.draw_part(airfoil, '0.001in', 'red', True, False )

    def draw_part_plan_side(self, airfoil ):
        self.draw_part(airfoil, '1px', 'red', True, False )

    def draw_part_demo(self, airfoil ):
        self.draw_part(airfoil, '1px', 'red', True, True )

    def draw_part_vertices(self, airfoil ):
        self.draw_part(airfoil, '1px', 'red', False, True )

    def save(self):
        for sheet in self.sheets:
            sheet.save()

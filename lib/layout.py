#!python

__author__ = "Curtis L. Olson < curtolson {at} flightgear {dot} org >"
__url__ = "http://gallinazo.flightgear.org"
__version__ = "1.0"
__license__ = "GPL v2"


import copy

import svgwrite

import airfoil


class Layout:

    def __init__(self, name, width_in, height_in, dpi):
        self.dwg = svgwrite.Drawing( name, size = ( '{:.2f}in'.format(width_in), '{:.2f}in'.format(height_in) ) )
        self.width_in = width_in
        self.height_in = height_in
        self.dpi = dpi

    def draw_airfoil(self, orig_airfoil, xpos, ypos, stroke_width, color, lines = True, points = False ):
        airfoil = copy.deepcopy(orig_airfoil)
        airfoil.scale(1,-1)
        bounds = airfoil.get_bounds()
        dx = bounds[1][0] - bounds[0][0]
        dy = bounds[1][1] - bounds[0][1]

        marginx = (self.width_in - dx) * 0.5
        marginy = (self.height_in - dy) * 0.5
    
        airfoil.scale( self.dpi, self.dpi )
        reverse_top = list(airfoil.top)
        reverse_top.reverse()
        shape = reverse_top + airfoil.bottom
        g = self.dwg.g()
        g.translate((marginx-bounds[0][0])*self.dpi,(ypos-bounds[0][1])*self.dpi)
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

    def draw_airfoil_cut(self, airfoil, xpos, ypos ):
        self.draw_airfoil(airfoil, xpos, ypos, '0.001in', 'red', True, False )

    def draw_airfoil_plan(self, airfoil, xpos, ypos ):
        self.draw_airfoil(airfoil, xpos, ypos, '1px', 'red', True, False )

    def draw_airfoil_demo(self, airfoil, xpos, ypos ):
        self.draw_airfoil(airfoil, xpos, ypos, '1px', 'red', True, True )

    def draw_airfoil_points(self, airfoil, xpos, ypos ):
        self.draw_airfoil(airfoil, xpos, ypos, '1px', 'red', False, True )

    def save(self):
        self.dwg.save()

#!/usr/bin/env python

try:
    import spline
except ImportError:
    # if airfoil is not 'installed' append parent dir of __file__ to sys.path
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/../lib'))
    import spline

points = ((0.0, 9.0), (5.0, 11.0), (10, 11.0), (30.0, 6.0))
y2 = spline.derivative2( points )
for x in range(0, 31, 1):
    index = spline.binsearch(points, x)
    y = spline.spline(points, y2, index, x)
    print str(x) + " " + str(y)


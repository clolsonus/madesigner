import subprocess
import sys

# path to your FreeCAD.so or FreeCAD.dll file
FREECADPATH = '/usr/lib64/freecad/lib'
sys.path.append(FREECADPATH)
import FreeCAD
import Part
from FreeCAD import Base

structure = Part.Compound

def make_object(name, poly, thickness, pos, nudge):
    norm = Base.Vector(0,thickness,0)
    object = None
    for i in range(len(poly)):
        pts = []
        for p in poly.contour(i):
            pts.append( Base.Vector(p[0], 0.0, p[1]) )
        # close the loop
        pts.append( pts[0] )
        print 'pts:', pts
        seg = Part.makePolygon( pts )
        face = Part.Face(seg)
        shape = face.extrude(norm)
        if poly.isHole(i):
            print 'hole:', poly.contour(i)
            if object:
                object = object.cut(shape)
        else:
            print 'outline:', poly.contour(i)
            if object:
                object = object.fuse(shape)
            else:
                object = shape
    return object

def add_object(part):
    structure.add(part)

def view_structure():
    structure.exportStl('junk.stl')
    command = ['osgviewer', 'junk.stl']
    pid = subprocess.Popen(command).pid
    print "spawned osgviewer with pid = " + str(pid)

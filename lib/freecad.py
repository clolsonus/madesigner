import subprocess
import sys

# path to your FreeCAD.so or FreeCAD.dll file
FREECADPATH = '/usr/lib64/freecad/lib'
sys.path.append(FREECADPATH)
import FreeCAD
import Part
from FreeCAD import Base

myDocument = FreeCAD.newDocument("Document Name")
myGroup = myDocument.addObject("App::DocumentObjectGroup","Group1")
parts = []

def make_extrusion(name, points, side="left"):
    wires = []
    for section in points:
        pts = []
        for pt in section:
            #print "%.2f %.2f %.2f" % (pt[0], pt[1], pt[2])
            pts.append( Base.Vector(pt[0], pt[1], pt[2]) )
        pts.append(Base.Vector(pts[0])) # close loop
        wire = Part.makePolygon(pts)
        wires.append(wire)
    loft = Part.makeLoft(wires, True)
    return loft
            

def make_object(name, poly, thickness, pos, nudge):
    print pos
    norm = Base.Vector(0,thickness,0)
    object = None
    for i in range(len(poly)):
        pts = []
        for p in poly.contour(i):
            pts.append( Base.Vector(p[0]+pos[1], 0.0+pos[0], p[1]+pos[2]) )
        # close the loop
        pts.append( pts[0] )
        #print 'pts:', pts
        seg = Part.makePolygon( pts )
        face = Part.Face(seg)
        shape = face.extrude(norm)
        if poly.isHole(i):
            #print 'hole:', poly.contour(i)
            if object:
                object = object.cut(shape)
        else:
            #print 'outline:', poly.contour(i)
            if object:
                object = object.fuse(shape)
            else:
                object = shape
    return object

def add_object(part):
    p = myDocument.addObject("Part::Feature", "some part")
    myGroup.addObject(p)
    p.Shape = part
    parts.append(part)

def view_structure():
    # merge all the faces from all the parts into a compound
    faces = []
    for part in parts:
        faces.extend(part.Faces)
    compound = Part.Compound(faces)

    # export to stl
    compound.exportStl('junk.stl')

    # view stl
    command = ['osgviewer', 'junk.stl']
    pid = subprocess.Popen(command).pid
    print "spawned osgviewer with pid = " + str(pid)

    # save our document
    myDocument.saveAs("test.FCStd")

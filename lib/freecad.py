import subprocess
import sys

# path to your FreeCAD.so or FreeCAD.dll file
FREECADPATH = '/usr/lib64/freecad/lib'
sys.path.append(FREECADPATH)
import FreeCAD
import Part
from FreeCAD import Base

class GenFreeCAD():
    def __init__(self):
        self.doc = None
        self.all_group = None
        self.kit_group = None
        self.stock_group = None
        self.extra_group = None

    def start_model(self, name):
        self.doc = FreeCAD.newDocument(name)
        self.kit_group = self.doc.addObject("App::DocumentObjectGroup", "Kit")
        self.stock_group = self.doc.addObject("App::DocumentObjectGroup", "Stock")
        self.all_group = self.doc.addObject("App::DocumentObjectGroup", "All")

    def save_model(self, name):
        self.doc.saveAs("test.FCStd")

    def make_extrusion(self, name, points):
        wires = []
        for section in points:
            pts = []
            for pt in section:
                # print "%.2f %.2f %.2f" % (pt[0], pt[1], pt[2])
                pts.append( Base.Vector(pt[0], pt[1], pt[2]) )
            pts.append(Base.Vector(pts[0])) # close loop
            wire = Part.makePolygon(pts)
            wires.append(wire)
        loft = Part.makeLoft(wires, True)
        return loft

    def make_object(self, poly, thickness, pos, nudge):
        #print pos
        halfw = thickness * 0.5
        norm = Base.Vector(0,thickness,0)
        object = None
        for i in range(len(poly)):
            pts = []
            for p in poly.contour(i):
                pts.append( Base.Vector(p[0]+pos[1], -halfw-nudge+pos[0], p[1]+pos[2]) )
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

    # make a new group and return it
    def make_extra_group(self, name):
        self.extra_group = self.doc.addObject("App::DocumentObjectGroup", name)

    def add_object(self, group, name, part):
        p = self.doc.addObject("Part::Feature", name)
        p.Shape = part
        if group == 'kit':
            self.kit_group.addObject(p)
        elif group == 'stock':
            self.stock_group.addObject(p)
        self.all_group.addObject(p)
        if self.extra_group:
            self.extra_group.addObject(p)

    def view_stl(self):
        # merge all the faces from all the parts into a compound
        face_list = []

        #for part in parts:
        #    faces.extend(part.Faces)

        for part in self.all_group.Group:
            shape = part.Shape
            faces = shape.Faces
            face_list.extend(faces)

        compound = Part.Compound(face_list)

        # export to stl
        compound.exportStl('junk.stl')

        # view stl
        command = ['osgviewer', 'junk.stl']
        pid = subprocess.Popen(command).pid
        print "spawned osgviewer with pid = " + str(pid)

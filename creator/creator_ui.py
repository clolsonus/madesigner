#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
MA creator 

This program hopefully does something eventually ...

author: Curtis L. Olson
website: madesigner.flightgear.org
started edited: November 2013
"""

import sys
import os.path
import subprocess
import distutils.spawn
from PyQt4 import QtGui, QtCore
import xml.etree.ElementTree as ET

from overview import Overview
from wing_ui import WingUI
from builder import Builder

class Creator(QtGui.QWidget):
    
    def __init__(self, filename):
        super(Creator, self).__init__()
        root = ET.Element('design')
        self.xml = ET.ElementTree(root)
        self.default_title = "Model Aircraft Creator"
        self.wings = []
        self.initUI()
        self.filename = None
        self.fileroot = None
        self.load(filename)

    def initUI(self):               
        self.setWindowTitle( self.default_title )

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        # 'File' button bar
        file_group = QtGui.QFrame()
        layout.addWidget(file_group)
        file_layout = QtGui.QHBoxLayout()
        file_group.setLayout( file_layout )

        new = QtGui.QPushButton('New')
        #new.clicked.connect(self.new_design)
        file_layout.addWidget(new)

        open = QtGui.QPushButton('Open...')
        open.clicked.connect(self.open)
        file_layout.addWidget(open)

        save = QtGui.QPushButton('Save')
        save.clicked.connect(self.save)
        file_layout.addWidget(save)

        saveas = QtGui.QPushButton('Save As...')
        saveas.clicked.connect(self.saveas)
        file_layout.addWidget(saveas)

        quit = QtGui.QPushButton('Quit')
        quit.clicked.connect(QtCore.QCoreApplication.instance().quit)
        file_layout.addWidget(quit)

        # Main work area
        self.tabs = QtGui.QTabWidget()
        layout.addWidget( self.tabs )

        self.overview = Overview()
        self.tabs.addTab( self.overview.get_widget(), "Overview" );

        # 'Command' button bar
        cmd_group = QtGui.QFrame()
        layout.addWidget(cmd_group)
        cmd_layout = QtGui.QHBoxLayout()
        cmd_group.setLayout( cmd_layout )

        add_wing = QtGui.QPushButton('Add Wing...')
        add_wing.clicked.connect(self.add_wing)
        cmd_layout.addWidget(add_wing)
  
        #add_fuse = QtGui.QPushButton('Add Fuselage...')
        #add_fuse.clicked.connect(self.add_fuse)
        #cmd_layout.addWidget(add_fuse)
  
        fast_build = QtGui.QPushButton('Fast Build...')
        fast_build.clicked.connect(self.build_fast)
        cmd_layout.addWidget(fast_build)
  
        detail_build = QtGui.QPushButton('Detail Build...')
        detail_build.clicked.connect(self.build_detail)
        cmd_layout.addWidget(detail_build)
  
        view3d = QtGui.QPushButton('View 3D')
        view3d.clicked.connect(self.view3d)
        cmd_layout.addWidget(view3d)
  
        cmd_layout.addStretch(1)

        self.resize(800, 900)
        self.show()

    def add_wing(self):
        wing = WingUI()
        self.wings.append(wing)
        self.tabs.addTab( wing.get_widget(), "Wing - New" )

    #def add_fuse(self):
    #    print "add fuse requested"

    def build_fast(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        build = Builder(filename=self.filename, airfoil_resample=25, \
                            circle_points=8)
        QtGui.QApplication.restoreOverrideCursor()

    def build_detail(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        build = Builder(filename=self.filename, airfoil_resample=1000, \
                            circle_points=32)
        QtGui.QApplication.restoreOverrideCursor()

    def view3d(self):
        viewer = "osgviewer"

        # look for viewer in the standard path
        result = distutils.spawn.find_executable(viewer)

        if result == None:
            viewer = os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+'/OpenSceneGraph/bin/osgviewer')
            print "testing for " + viewer
            result = os.path.isfile(viewer)

        if not result:
            error = QtGui.QErrorMessage(self)
            error.showMessage( "Cannot find " + viewer + " in path.  Perhaps it needs to be installed?" )
        else:
            command = []
            command.append(viewer)
            command.append("--window")
            command.append("0")
            command.append("0")
            command.append("800")
            command.append("600")
            command.append(self.fileroot + ".ac")
            pid = subprocess.Popen(command).pid
            print "spawned osgviewer with pid = " + str(pid)
 
    def load(self, filename):
        basename = os.path.basename(str(filename))
        fileroot, ext = os.path.splitext(basename)

        if not os.path.exists(filename):
            #print "new empty design: " + filename
            return

        try:
            self.xml = ET.parse(filename)
        except:
            error = QtGui.QErrorMessage(self)
            error.showMessage( filename + ": xml parse error:\n" + str(sys.exc_info()[1]) )
            return

        if filename != "":
            self.setWindowTitle( self.default_title + " - " + fileroot )

        self.filename = str(filename)
        self.fileroot, ext = os.path.splitext(self.filename)

        root = self.xml.getroot()
        node = root.find('overview')
        self.overview.parse_xml(node)

        for wing_node in root.findall('wing'):
            wing = WingUI()
            wing.parse_xml(wing_node)
            self.wings.append(wing)
            self.tabs.addTab( wing.get_widget(), "Wing - " + wing.get_name() )

    def open(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", "",
                                                     "MAdesigner (*.mad)")
        if ( filename == "" ):
            return
        self.load(filename)

    def setFileName(self):
        return QtGui.QFileDialog.getSaveFileName(self, "Save File",
                                                 "newdesign.mad",
                                                 "MAdesigner (*.mad)")

    def save(self):
        if self.filename == "":
            filename = self.setFileName()
            if filename == "":
                print "cancelled save ..."
                return
            else:
                self.filename = filename
                self.fileroot, ext = os.path.splitexe(self.filename)

        # create a new xml root
        root = ET.Element('design')
        self.xml = ET.ElementTree(root)

        # overview
        node = ET.SubElement(root, 'overview')
        self.overview.gen_xml(node)

        # wings
        for wing in self.wings:
            if wing.valid:
                node = ET.SubElement(root, 'wing')
                wing.gen_xml(node)

        try:
            self.xml.write(self.filename, encoding="us-ascii",
                           xml_declaration=False)
        except:
            print "error saving file"
            return

        self.setWindowTitle( self.default_title + " - " + os.path.basename(str(self.filename)) )

    def saveas(self):
        filename = self.setFileName()

        if filename == "":
            print "cancelled save as ..."
            return
        else:
            self.filename = str(filename)
            self.fileroot, ext = os.path.splitext(self.filename)

        self.save()

def usage():
    print "Usage: " + sys.argv[0] + " [design.mad]"

def main():
    app = QtGui.QApplication(sys.argv)
    filename = ""
    if len(sys.argv) > 2:
        usage()
        return
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
    ex = Creator(filename)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

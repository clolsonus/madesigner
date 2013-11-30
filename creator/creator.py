#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
MAcreator 

This program hopefully does something eventually ...

author: Curtis L. Olson
website: madesigner.flightgear.org
started edited: November 2013
"""

import sys
import os.path
from PyQt4 import QtGui, QtCore
import xml.etree.ElementTree as ET

from overview import Overview
from wing import Wing

class Creator(QtGui.QWidget):
    
    def __init__(self, initfile):
        super(Creator, self).__init__()
        root = ET.Element('design')
        self.xml = ET.ElementTree(root)
        self.default_title = "Model Aircraft Creator"
        self.wings = []
        self.initUI()
        self.load(initfile)

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
        #quit.clicked.connect(QtCore.QCoreApplication.instance().quit)
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
  
        build = QtGui.QPushButton('Build...')
        build.clicked.connect(self.build)
        cmd_layout.addWidget(build)
  
        self.setGeometry(300, 300, 250, 150)
        self.show()

    def add_wing(self):
        wing_page = Wing()
        self.wings.append(wing_page)
        self.tabs.addTab( wing_page.get_widget(),
                          "Wing - New" );

    #def add_fuse(self):
    #    print "add fuse requested"

    def build(self):
        print "build requested"

    def load(self, filename):
        self.filename = filename
        if not os.path.exists(filename):
            print "new empty design: " + filename
            return

        try:
            self.xml = ET.parse(filename)
        except:
            print filename + ": xml parse error"
            return

        self.setWindowTitle( self.default_title + " - "
                             + os.path.basename(str(self.filename)) )

        root = self.xml.getroot()
        node = root.find('overview')
        self.overview.parse_xml(node)

        for wing in root.findall('wing'):
            wing_page = Wing()
            wing_page.parse_xml(wing)
            self.wings.append(wing_page)
            self.tabs.addTab( wing_page.get_widget(),
                              "Wing - " + wing_page.get_name() );

    def open(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", "", "MAdesigner (*.mad)")
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

        # create a new xml root
        root = ET.Element('design')
        self.xml = ET.ElementTree(root)

        # overview
        node = ET.SubElement(root, 'overview')
        self.overview.gen_xml(node)

        # wings
        for index, wing in enumerate(self.wings):
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
            self.filename = filename

        self.save()

def usage():
    print "Usage: " + sys.argv[0] + " [design.mad]"

def main():
    app = QtGui.QApplication(sys.argv)
    initfile = ""
    if len(sys.argv) > 2:
        usage()
        return
    elif len(sys.argv) == 2:
        initfile = sys.argv[1]
    ex = Creator(initfile)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

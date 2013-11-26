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


class Creator(QtGui.QWidget):
    
    def __init__(self):
        super(Creator, self).__init__()
        self.filename = ""
        root = ET.Element('design')
        self.xml = ET.ElementTree(root)
        self.default_title = "Model Aircraft Creator"
        self.initUI()
        
    def initUI(self):               

        self.setWindowTitle( self.default_title )

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        tabs = QtGui.QTabWidget()
        layout.addWidget( tabs )

        self.overview = Overview()
        tabs.addTab( self.overview.widget(), "Overview" );

        bgroup = QtGui.QFrame()
        layout.addWidget(bgroup)
        blayout = QtGui.QHBoxLayout()
        bgroup.setLayout( blayout )

        new = QtGui.QPushButton('New')
        #quit.clicked.connect(QtCore.QCoreApplication.instance().quit)
        blayout.addWidget(new)

        open = QtGui.QPushButton('Open...')
        open.clicked.connect(self.open)
        blayout.addWidget(open)

        save = QtGui.QPushButton('Save')
        save.clicked.connect(self.save)
        blayout.addWidget(save)

        saveas = QtGui.QPushButton('Save As...')
        saveas.clicked.connect(self.saveas)
        blayout.addWidget(saveas)

        quit = QtGui.QPushButton('Quit')
        quit.clicked.connect(QtCore.QCoreApplication.instance().quit)
        blayout.addWidget(quit)

        self.setGeometry(300, 300, 250, 150)
        self.show()

    def open(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", "", "MAdesigner (*.mad)")
        if ( filename != "" ):
            self.filename = filename
        else:
            return
        try:
            self.xml = ET.parse(filename)
        except:
            print "xml parse error"
            return

        self.setWindowTitle( self.default_title + " - " + os.path.basename(str(self.filename)) )

        root = self.xml.getroot()
        node = root.find('overview')
        self.overview.parse_xml(node)

    def setFileName(self):
        return QtGui.QFileDialog.getSaveFileName(self, "Save File", "newdesign.mad", "MAdesigner (*.mad)")

    def save(self):
        if self.filename == "":
            filename = self.setFileName()
            if filename == "":
                print "cancelled save ..."
                return
            else:
                self.filename = filename

        root = self.xml.getroot()
        node = root.find('overview')
        if node == None:
            node = ET.SubElement(root, 'overview')
        self.overview.gen_xml(node)
        #ET.dump(self.xml)
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

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Creator()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

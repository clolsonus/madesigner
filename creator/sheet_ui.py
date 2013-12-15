#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Sheet

author: Curtis L. Olson
website: madesigner.flightgear.org
started: December 2013
"""

import sys
from PyQt4 import QtGui, QtCore
import xml.etree.ElementTree as ET
from combobox_nowheel import QComboBoxNoWheel


class SheetUI():
    def __init__(self):
        self.valid = True
        self.container = self.make_page()
        self.xml = None
        self.clean = True

    def onChange(self):
        self.clean = False

    def isClean(self):
        return self.clean

    def setClean(self):
        self.clean = True

    def rebuild_stations(self, stations):
        station_list = str(stations).split()
        start_text = self.edit_start.currentText()
        end_text = self.edit_end.currentText()
        self.edit_start.clear()
        self.edit_start.addItem("Start: Inner")
        self.edit_end.clear()
        self.edit_end.addItem("End: Outer")
        for index,station in enumerate(station_list):
            text = "Start: " + str(station)
            self.edit_start.addItem(text)
            text = "End: " + str(station)
            self.edit_end.addItem(text)
        index = self.edit_start.findText(start_text)
        if index != None:
            self.edit_start.setCurrentIndex(index)
        index = self.edit_end.findText(end_text)
        if index != None:
            self.edit_end.setCurrentIndex(index)

    def delete_self(self):
        #print "delete self!"
        self.container.deleteLater()
        self.clean = False
        self.valid = False

    def make_page(self):
        page = QtGui.QFrame()
        layout = QtGui.QVBoxLayout()
        page.setLayout( layout )

        line1 = QtGui.QFrame()
        layout1 = QtGui.QHBoxLayout()
        line1.setLayout( layout1 )
        layout.addWidget( line1 )

        line2 = QtGui.QFrame()
        layout2 = QtGui.QHBoxLayout()
        line2.setLayout( layout2 )
        layout.addWidget( line2 )

        layout1.addWidget( QtGui.QLabel("<b>Depth:</b> ") )

        self.edit_depth = QtGui.QLineEdit()
        self.edit_depth.setFixedWidth(70)
        self.edit_depth.textChanged.connect(self.onChange)
        layout1.addWidget( self.edit_depth )

        self.edit_start = QComboBoxNoWheel()
        self.edit_start.addItem("-")
        self.edit_start.addItem("1")
        self.edit_start.addItem("2")
        self.edit_start.addItem("3")
        self.edit_start.currentIndexChanged.connect(self.onChange)
        layout1.addWidget(self.edit_start)

        self.edit_end = QComboBoxNoWheel()
        self.edit_end.addItem("-")
        self.edit_end.addItem("1")
        self.edit_end.addItem("2")
        self.edit_end.addItem("3")
        self.edit_end.currentIndexChanged.connect(self.onChange)
        layout1.addWidget(self.edit_end)

        delete = QtGui.QPushButton('Delete')
        delete.clicked.connect(self.delete_self)
        layout1.addWidget(delete)
  
        layout1.addStretch(1)

        layout2.addWidget( QtGui.QLabel("<b>Start Pos:</b> ") )

        self.edit_xstart = QtGui.QLineEdit()
        self.edit_xstart.setFixedWidth(50)
        self.edit_xstart.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_xstart )

        self.edit_xmode = QComboBoxNoWheel()
        self.edit_xmode.addItem("Sheet Width")
        self.edit_xmode.addItem("End Position")
        self.edit_xmode.currentIndexChanged.connect(self.onChange)
        layout2.addWidget(self.edit_xmode)

        self.edit_xend = QtGui.QLineEdit()
        self.edit_xend.setFixedWidth(50)
        self.edit_xend.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_xend )

        self.edit_surface = QComboBoxNoWheel()
        self.edit_surface.addItem("Top")
        self.edit_surface.addItem("Bottom")
        self.edit_surface.currentIndexChanged.connect(self.onChange)
        layout2.addWidget(self.edit_surface)

        layout2.addStretch(1)

        return page

    def get_widget(self):
        return self.container

    def get_value(self, node):
        e = self.xml.find(node)
        if e != None and e.text != None:
            return e.text
        else:
            return ""

    def parse_xml(self, node):
        self.xml = node
        self.edit_depth.setText(self.get_value('depth'))
        self.edit_xstart.setText(self.get_value('xstart'))
        index = self.edit_xmode.findText(self.get_value('xmode'))
        if index == None:
            index = 1
        self.edit_xmode.setCurrentIndex(index)
        self.edit_xend.setText(self.get_value('xend'))
        index = self.edit_surface.findText(self.get_value('surface'))
        if index == None:
            index = 1
        self.edit_surface.setCurrentIndex(index)
        index = self.edit_start.findText(self.get_value('start-station'))
        if index != None:
            self.edit_start.setCurrentIndex(index)
        index = self.edit_end.findText(self.get_value('end-station'))
        if index != None:
            self.edit_end.setCurrentIndex(index)

    def update_node(self, node, value):
        e = self.xml.find(node)
        if e == None:
            e = ET.SubElement(self.xml, node)
        e.text = str(value)
        
    def gen_xml(self, node):
        self.xml = node
        self.update_node('depth', self.edit_depth.text())
        self.update_node('xstart', self.edit_xstart.text())
        self.update_node('xmode', self.edit_xmode.currentText())
        self.update_node('xend', self.edit_xend.text())
        self.update_node('surface', self.edit_surface.currentText())
        self.update_node('start-station', self.edit_start.currentText())
        self.update_node('end-station', self.edit_end.currentText())

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Spar

author: Curtis L. Olson
website: madesigner.flightgear.org
started: November 2013
"""

import sys
from PyQt4 import QtGui, QtCore
import xml.etree.ElementTree as ET
from combobox_nowheel import QComboBoxNoWheel


class ShapedHoleUI():
    def __init__(self):
        self.valid = True
        self.container = self.make_page()
        self.xml = None

    def onChange(self):
        # do nothing right now
        a = 0

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
        print "delete self!"
        self.container.deleteLater()
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

        layout1.addWidget( QtGui.QLabel("<b>Mat. W:</b> ") )

        self.edit_width = QtGui.QLineEdit()
        self.edit_width.setFixedWidth(50)
        self.edit_width.textChanged.connect(self.onChange)
        layout1.addWidget( self.edit_width )

        layout1.addWidget( QtGui.QLabel("<b>Corner Rad:</b> ") )

        self.edit_radius = QtGui.QLineEdit()
        self.edit_radius.setFixedWidth(50)
        self.edit_radius.textChanged.connect(self.onChange)
        layout1.addWidget( self.edit_radius )

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

        self.edit_pos1ref = QComboBoxNoWheel()
        self.edit_pos1ref.addItem("Chord %")
        self.edit_pos1ref.addItem("Rel Front")
        self.edit_pos1ref.addItem("Rel Rear")
        self.edit_pos1ref.addItem("Abs Pos")
        self.edit_pos1ref.currentIndexChanged.connect(self.onChange)
        layout2.addWidget(self.edit_pos1ref)

        self.edit_pos1 = QtGui.QLineEdit()
        self.edit_pos1.setFixedWidth(50)
        self.edit_pos1.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_pos1 )

        layout2.addWidget( QtGui.QLabel("<b>End Pos:</b> ") )

        self.edit_pos2ref = QComboBoxNoWheel()
        self.edit_pos2ref.addItem("Chord %")
        self.edit_pos2ref.addItem("Rel Front")
        self.edit_pos2ref.addItem("Rel Rear")
        self.edit_pos2ref.addItem("Abs Pos")
        self.edit_pos2ref.currentIndexChanged.connect(self.onChange)
        layout2.addWidget(self.edit_pos2ref)

        self.edit_pos2 = QtGui.QLineEdit()
        self.edit_pos2.setFixedWidth(50)
        self.edit_pos2.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_pos2 )

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
        self.edit_width.setText(self.get_value('material-width'))
        self.edit_radius.setText(self.get_value('corner-radius'))
        index = self.edit_pos1ref.findText(self.get_value('position1-ref'))
        if index == None:
            index = 1
        self.edit_pos1ref.setCurrentIndex(index)
        self.edit_pos1.setText(self.get_value('position1'))
        index = self.edit_pos2ref.findText(self.get_value('position2-ref'))
        if index == None:
            index = 1
        self.edit_pos2ref.setCurrentIndex(index)
        self.edit_pos2.setText(self.get_value('position2'))
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
        self.update_node('material-width', self.edit_width.text())
        self.update_node('corner-radius', self.edit_radius.text())
        self.update_node('position1-ref', self.edit_pos1ref.currentText())
        self.update_node('position1', self.edit_pos1.text())
        self.update_node('position2-ref', self.edit_pos2ref.currentText())
        self.update_node('position2', self.edit_pos2.text())
        self.update_node('start-station', self.edit_start.currentText())
        self.update_node('end-station', self.edit_end.currentText())

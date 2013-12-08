#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Trailing Edge

author: Curtis L. Olson
website: madesigner.flightgear.org
started: November 2013
"""

import sys
from PyQt4 import QtGui, QtCore
import xml.etree.ElementTree as ET
from combobox_nowheel import QComboBoxNoWheel


class TrailingEdgeUI():
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
        # make the edit line
        page = QtGui.QFrame()
        layout = QtGui.QHBoxLayout()
        page.setLayout( layout )

        layout.addWidget( QtGui.QLabel("<b>W x H:</b> ") )

        self.edit_width = QtGui.QLineEdit()
        self.edit_width.setFixedWidth(50)
        self.edit_width.textChanged.connect(self.onChange)
        layout.addWidget( self.edit_width )

        self.edit_height = QtGui.QLineEdit()
        self.edit_height.setFixedWidth(50)
        self.edit_height.textChanged.connect(self.onChange)
        layout.addWidget( self.edit_height )

        self.edit_shape = QComboBoxNoWheel()
        self.edit_shape.addItem("Flat")
        self.edit_shape.addItem("Symmetrical")
        layout.addWidget(self.edit_shape)

        self.edit_start = QComboBoxNoWheel()
        self.edit_start.addItem("-")
        self.edit_start.addItem("1")
        self.edit_start.addItem("2")
        self.edit_start.addItem("3")
        layout.addWidget(self.edit_start)

        self.edit_end = QComboBoxNoWheel()
        self.edit_end.addItem("-")
        self.edit_end.addItem("1")
        self.edit_end.addItem("2")
        self.edit_end.addItem("3")
        layout.addWidget(self.edit_end)

        delete = QtGui.QPushButton('Delete ')
        delete.clicked.connect(self.delete_self)
        layout.addWidget(delete)

        layout.addStretch(1)

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
        self.edit_width.setText(self.get_value('width'))
        self.edit_height.setText(self.get_value('height'))
        index = self.edit_shape.findText(self.get_value('shape'))
        if index == None:
            index = 1
        self.edit_shape.setCurrentIndex(index)
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
        self.update_node('width', self.edit_width.text())
        self.update_node('height', self.edit_height.text())
        self.update_node('shape', self.edit_shape.currentText())
        self.update_node('start-station', self.edit_start.currentText())
        self.update_node('end-station', self.edit_end.currentText())

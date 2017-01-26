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

from props import root, getNode

from combobox_nowheel import QComboBoxNoWheel


class SparUI():
    def __init__(self, changefunc):
        self.valid = True
        self.changefunc = changefunc
        self.container = self.make_page()

    def onChange(self):
        self.changefunc()

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
        if self.valid:
            self.changefunc()
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

        layout1.addWidget( QtGui.QLabel("<b>W x H:</b> ") )

        self.edit_width = QtGui.QLineEdit()
        self.edit_width.setFixedWidth(50)
        self.edit_width.textChanged.connect(self.onChange)
        layout1.addWidget( self.edit_width )

        self.edit_height = QtGui.QLineEdit()
        self.edit_height.setFixedWidth(50)
        self.edit_height.textChanged.connect(self.onChange)
        layout1.addWidget( self.edit_height )

        #self.edit_orientation = QComboBoxNoWheel()
        #self.edit_orientation.addItem("Vertical")
        #self.edit_orientation.addItem("Tangent")
        #self.edit_orientation.currentIndexChanged.connect(self.onChange)
        #layout1.addWidget(self.edit_orientation)

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

        layout1.addStretch(1)

        delete = QtGui.QPushButton('Delete')
        delete.clicked.connect(self.delete_self)
        layout1.addWidget(delete)
  
        layout2.addWidget( QtGui.QLabel("<b>Pos:</b> ") )

        self.edit_posref = QComboBoxNoWheel()
        self.edit_posref.addItem("Chord %")
        self.edit_posref.addItem("Rel Front")
        self.edit_posref.addItem("Rel Rear")
        self.edit_posref.addItem("Abs Pos")
        self.edit_posref.currentIndexChanged.connect(self.onChange)
        layout2.addWidget(self.edit_posref)

        self.edit_pos = QtGui.QLineEdit()
        self.edit_pos.setFixedWidth(50)
        self.edit_pos.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_pos )

        self.edit_surface = QComboBoxNoWheel()
        self.edit_surface.addItem("Top")
        self.edit_surface.addItem("Bottom")
        self.edit_surface.currentIndexChanged.connect(self.onChange)
        layout2.addWidget(self.edit_surface)

        layout2.addStretch(1)

        return page

    def get_widget(self):
        return self.container

    def parse_xml(self, node):
        self.edit_width.setText(node.getString('width'))
        self.edit_height.setText(node.getString('height'))
        index = self.edit_posref.findText(node.getString('position_ref'))
        if index == None:
            index = 1
        self.edit_posref.setCurrentIndex(index)
        self.edit_pos.setText(node.getString('position'))
        index = self.edit_surface.findText(node.getString('surface'))
        if index == None:
            index = 1
        self.edit_surface.setCurrentIndex(index)
        index = self.edit_start.findText(node.getString('start_station'))
        if index != None:
            self.edit_start.setCurrentIndex(index)
        index = self.edit_end.findText(node.getString('end_station'))
        if index != None:
            self.edit_end.setCurrentIndex(index)

    def gen_xml(self, node):
        node.setString('width', self.edit_width.text())
        node.setString('height', self.edit_height.text())
        node.setString('position_ref', self.edit_posref.currentText())
        node.setString('position', self.edit_pos.text())
        node.setString('surface', self.edit_surface.currentText())
        node.setString('start_station', self.edit_start.currentText())
        node.setString('end_station', self.edit_end.currentText())

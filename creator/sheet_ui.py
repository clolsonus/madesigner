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

from props import root, getNode

from combobox_nowheel import QComboBoxNoWheel


class SheetUI():
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

        layout1.addStretch(1)

        delete = QtGui.QPushButton('Delete')
        delete.clicked.connect(self.delete_self)
        layout1.addWidget(delete)
  
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

    def load(self, node):
        self.edit_depth.setText(node.getString('depth'))
        self.edit_xstart.setText(node.getString('xstart'))
        index = self.edit_xmode.findText(node.getString('xmode'))
        if index == None:
            index = 1
        self.edit_xmode.setCurrentIndex(index)
        self.edit_xend.setText(node.getString('xend'))
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

    def save(self, node):
        node.setString('depth', self.edit_depth.text())
        node.setString('xstart', self.edit_xstart.text())
        node.setString('xmode', self.edit_xmode.currentText())
        node.setString('xend', self.edit_xend.text())
        node.setString('surface', self.edit_surface.currentText())
        node.setString('start_station', self.edit_start.currentText())
        node.setString('end_station', self.edit_end.currentText())

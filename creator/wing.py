#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Wing Panel tab

author: Curtis L. Olson
website: madesigner.flightgear.org
started: November 2013
"""

import sys
from PyQt4 import QtGui, QtCore
import xml.etree.ElementTree as ET


class Wing():
    def __init__(self):
        self.container = self.make_page()
        self.xml = None

    def onChange(self):
        # do nothing right now
        a = 0

    def make_page(self):
        # make the full edit widget
        page = QtGui.QFrame()
        layout = QtGui.QFormLayout()
        page.setLayout( layout )

        self.edit_name = QtGui.QLineEdit()
        self.edit_name.setFixedWidth(250)
        self.edit_name.textChanged.connect(self.onChange)
        self.edit_name.setText("New")
        self.edit_airfoil = QtGui.QLineEdit()
        self.edit_airfoil.setFixedWidth(250)
        self.edit_airfoil.textChanged.connect(self.onChange)
        self.edit_length = QtGui.QLineEdit()
        self.edit_length.setFixedWidth(250)
        self.edit_length.textChanged.connect(self.onChange)
        self.edit_chord = QtGui.QLineEdit()
        self.edit_chord.setFixedWidth(250)
        self.edit_chord.textChanged.connect(self.onChange)

        layout.addRow( "<b>Wing Name:</b>", self.edit_name )
        layout.addRow( "<b>Airfoil(s):</b>", self.edit_airfoil )
        layout.addRow( "<b>Length:</b>", self.edit_length )
        layout.addRow( "<b>Chord:</b>", self.edit_chord )

        return page

    def get_widget(self):
        return self.container

    def get_name(self):
        return self.edit_name.text()

    def get_value(self, node):
        e = self.xml.find(node)
        if e != None and e.text != None:
            return e.text
        else:
            return ""

    def parse_xml(self, node):
        self.xml = node
        self.edit_name.setText(self.get_value('name'))
        self.edit_airfoil.setText(self.get_value('airfoil'))
        self.edit_length.setText(self.get_value('length'))
        self.edit_chord.setText(self.get_value('chord'))

    def update_node(self, node, value):
        e = self.xml.find(node)
        if e == None:
            e = ET.SubElement(self.xml, node)
        e.text = str(value)
        
    def gen_xml(self, node):
        self.xml = node
        self.update_node('name', self.edit_name.text())
        self.update_node('airfoil', self.edit_airfoil.text())
        self.update_node('length', self.edit_length.text())
        self.update_node('chord', self.edit_chord.text())


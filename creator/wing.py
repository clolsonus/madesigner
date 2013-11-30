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
        self.valid = True
        self.container = self.make_page()
        self.xml = None

    def onChange(self):
        # do nothing right now
        a = 0

    def add_leading_edge(self):
        print "add leading edge"

    def add_trailing_edge(self):
        print "add trailing edge"

    def add_spar(self):
        print "add spar"

    def add_stringer(self):
        print "add stringer"

    def add_sheeting(self):
        print "add sheeting"

    def add_simple_hole(self):
        print "add simple hole"

    def add_shaped_hole(self):
        print "add simple hole"

    def add_build_tab(self):
        print "add build tab"

    def add_flap(self):
        print "add flap"

    def delete_self(self):
        print "delete self!"
        self.container.deleteLater()
        self.valid = False

    def make_page(self):
        # make the full edit widget
        page = QtGui.QFrame()
        layout = QtGui.QVBoxLayout()
        page.setLayout(layout)

        contents = QtGui.QFrame()
        formlayout = QtGui.QFormLayout()
        contents.setLayout( formlayout )

        scroll = QtGui.QScrollArea()
        scroll.setWidget(contents)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # 'Command' button bar
        cmd_group = QtGui.QFrame()
        layout.addWidget(cmd_group)
        cmd_layout = QtGui.QHBoxLayout()
        cmd_group.setLayout( cmd_layout )

        add_part = QtGui.QPushButton("Add Structure ...")
        menu = QtGui.QMenu()
        menu.addAction("Leading Edge", self.add_leading_edge)
        menu.addAction("Trailing Edge", self.add_trailing_edge)
        menu.addAction("Spar", self.add_spar)
        menu.addAction("Stringer", self.add_stringer)
        menu.addAction("Sheeting", self.add_sheeting)
        menu.addAction("Lighting/Spar Hole", self.add_simple_hole)
        menu.addAction("Shaped Hole", self.add_shaped_hole)
        menu.addAction("Build Tab", self.add_build_tab)
        menu.addAction("Add Control Surface", self.add_flap)
        add_part.setMenu(menu)
        cmd_layout.addWidget(add_part)

        #add_le.clicked.connect(self.add_leading_edge)
        #add_te.clicked.connect(self.add_trailing_edge)
        #add_spar.clicked.connect(self.add_spar)
        #add_stringer.clicked.connect(self.add_stringer)

        delete = QtGui.QPushButton('Delete Wing')
        delete.clicked.connect(self.delete_self)
        cmd_layout.addWidget(delete)
  

        # form content
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
        self.edit_twist = QtGui.QLineEdit()
        self.edit_twist.setFixedWidth(250)
        self.edit_twist.textChanged.connect(self.onChange)
        self.edit_sweep = QtGui.QLineEdit()
        self.edit_sweep.setFixedWidth(250)
        self.edit_sweep.textChanged.connect(self.onChange)
        self.edit_dihedral = QtGui.QLineEdit()
        self.edit_dihedral.setFixedWidth(250)
        self.edit_dihedral.textChanged.connect(self.onChange)
        self.edit_stations = QtGui.QLineEdit()
        self.edit_stations.setFixedWidth(250)
        self.edit_stations.textChanged.connect(self.onChange)

        formlayout.addRow( "<b>Wing Name:</b>", self.edit_name )
        formlayout.addRow( "<b>Airfoil(s):</b>", self.edit_airfoil )
        formlayout.addRow( "<b>Length:</b>", self.edit_length )
        formlayout.addRow( "<b>Chord:</b>", self.edit_chord )
        formlayout.addRow( "<b>Twist/Washout (deg):</b>", self.edit_twist )
        formlayout.addRow( "<b>Sweep (deg):</b>", self.edit_sweep )
        formlayout.addRow( "<b>Dihedral (deg):</b>", self.edit_dihedral )
        formlayout.addRow( "<b>Stations:</b>", self.edit_stations )

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
        self.edit_twist.setText(self.get_value('twist'))
        self.edit_sweep.setText(self.get_value('sweep'))
        self.edit_dihedral.setText(self.get_value('dihedral'))
        self.edit_stations.setText(self.get_value('stations'))

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
        self.update_node('twist', self.edit_twist.text())
        self.update_node('sweep', self.edit_sweep.text())
        self.update_node('dihedral', self.edit_dihedral.text())
        self.update_node('stations', self.edit_stations.text())


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
from leading_edge import LeadingEdge


class Wing():
    def __init__(self):
        self.valid = True
        self.container = self.make_page()
        self.xml = None
        self.leading_edges = []
        self.trailing_edges = []
        self.spars = []
        self.stringers = []
        self.sheets = []
        self.simple_holes = []
        self.shaped_holes = []
        self.build_tabs = []
        self.flaps = []

    def onChange(self):
        # do nothing right now
        a = 0

    def rebuildStations(self):
        # rebuild stations when station list has changed
        for le in self.leading_edges:
            if le.valid:
                le.rebuild_stations(self.edit_stations.text())

    def add_leading_edge(self, xml_node=None):
        print "add leading edge"
        leading_edge = LeadingEdge()
        leading_edge.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            leading_edge.parse_xml(xml_node)
        self.leading_edges.append(leading_edge)
        self.layout_le.addWidget( leading_edge.get_widget() )


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
        toppage = QtGui.QFrame()
        toplayout = QtGui.QVBoxLayout()
        toppage.setLayout(toplayout)

        page = QtGui.QFrame()
        layout = QtGui.QVBoxLayout()
        page.setLayout(layout)

        maincontents = QtGui.QFrame()
        formlayout = QtGui.QFormLayout()
        maincontents.setLayout( formlayout )
        layout.addWidget(maincontents)

        scroll = QtGui.QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        #layout.addWidget(scroll)
        toplayout.addWidget(scroll)

        self.group_flaps = QtGui.QGroupBox("Control Surfaces")
        layout.addWidget(self.group_flaps)

        frame = QtGui.QGroupBox("Leading Edges")
        self.layout_le = QtGui.QVBoxLayout()
        frame.setLayout(self.layout_le)
        layout.addWidget(frame)

        frame = QtGui.QGroupBox("Trailing Edges")
        self.layout_te = QtGui.QVBoxLayout()
        frame.setLayout(self.layout_te)
        layout.addWidget(frame)

        frame = QtGui.QGroupBox("Spars")
        self.layout_spars = QtGui.QVBoxLayout()
        frame.setLayout(self.layout_spars)
        layout.addWidget(frame)

        frame = QtGui.QGroupBox("Stringers")
        self.layout_stringers = QtGui.QVBoxLayout()
        frame.setLayout(self.layout_stringers)
        layout.addWidget(frame)

        frame = QtGui.QGroupBox("Sheeting")
        self.layout_sheeting = QtGui.QVBoxLayout()
        frame.setLayout(self.layout_sheeting)
        layout.addWidget(frame)

        frame = QtGui.QGroupBox("Simple Holes")
        self.layout_simple_holes = QtGui.QVBoxLayout()
        frame.setLayout(self.layout_simple_holes)
        layout.addWidget(frame)

        frame = QtGui.QGroupBox("Shaped Holes")
        self.layout_shaped_holes = QtGui.QVBoxLayout()
        frame.setLayout(self.layout_shaped_holes)
        layout.addWidget(frame)

        frame = QtGui.QGroupBox("Build Tabs")
        self.layout_build_tabs = QtGui.QVBoxLayout()
        frame.setLayout(self.layout_build_tabs)
        layout.addWidget(frame)

        # 'Command' button bar
        cmd_group = QtGui.QFrame()
        toplayout.addWidget(cmd_group)
        cmd_layout = QtGui.QHBoxLayout()
        cmd_group.setLayout( cmd_layout )

        add_feature = QtGui.QPushButton("Add Feature ...")
        menu = QtGui.QMenu()
        menu.addAction("Add Control Surface", self.add_flap)
        menu.addAction("Leading Edge", self.add_leading_edge)
        menu.addAction("Trailing Edge", self.add_trailing_edge)
        menu.addAction("Spar", self.add_spar)
        menu.addAction("Stringer", self.add_stringer)
        menu.addAction("Sheeting", self.add_sheeting)
        menu.addAction("Lighting/Spar Hole", self.add_simple_hole)
        menu.addAction("Shaped Hole", self.add_shaped_hole)
        menu.addAction("Build Tab", self.add_build_tab)
        add_feature.setMenu(menu)
        cmd_layout.addWidget(add_feature)

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
        self.edit_stations.textChanged.connect(self.rebuildStations)

        formlayout.addRow( "<b>Wing Name:</b>", self.edit_name )
        formlayout.addRow( "<b>Airfoil(s):</b>", self.edit_airfoil )
        formlayout.addRow( "<b>Length:</b>", self.edit_length )
        formlayout.addRow( "<b>Chord:</b>", self.edit_chord )
        formlayout.addRow( "<b>Twist/Washout (deg):</b>", self.edit_twist )
        formlayout.addRow( "<b>Sweep (deg):</b>", self.edit_sweep )
        formlayout.addRow( "<b>Dihedral (deg):</b>", self.edit_dihedral )
        formlayout.addRow( "<b>Stations:</b>", self.edit_stations )

        return toppage

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

        for le_node in node.findall('leading-edge'):
            self.add_leading_edge(le_node)

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

        for le in self.leading_edges:
            if le.valid:
                subnode = ET.SubElement(node, 'leading-edge')
                le.gen_xml(subnode)



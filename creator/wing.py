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
from trailing_edge import TrailingEdge
from spar import Spar
from sheet import Sheet
from simple_hole import SimpleHole
from shaped_hole import ShapedHole
from build_tab import BuildTab


class Wing():
    def __init__(self):
        self.valid = True
        self.container = self.make_page()
        self.xml = None
        self.leading_edges = []
        self.trailing_edges = []
        self.spars = []
        self.stringers = []
        self.sheeting = []
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
        for te in self.trailing_edges:
            if te.valid:
                te.rebuild_stations(self.edit_stations.text())
        for spar in self.spars:
            if spar.valid:
                spar.rebuild_stations(self.edit_stations.text())
        for stringer in self.stringers:
            if stringer.valid:
                stringer.rebuild_stations(self.edit_stations.text())
        for sheet in self.sheeting:
            if sheet.valid:
                sheet.rebuild_stations(self.edit_stations.text())
        for hole in self.simple_holes:
            if hole.valid:
                hole.rebuild_stations(self.edit_stations.text())
        for hole in self.shaped_holes:
            if hole.valid:
                hole.rebuild_stations(self.edit_stations.text())
        for tab in self.build_tabs:
            if tab.valid:
                tab.rebuild_stations(self.edit_stations.text())

    def add_leading_edge(self, xml_node=None):
        leading_edge = LeadingEdge()
        leading_edge.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            leading_edge.parse_xml(xml_node)
        self.leading_edges.append(leading_edge)
        self.layout_le.addWidget( leading_edge.get_widget() )


    def add_trailing_edge(self, xml_node=None):
        trailing_edge = TrailingEdge()
        trailing_edge.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            trailing_edge.parse_xml(xml_node)
        self.trailing_edges.append(trailing_edge)
        self.layout_te.addWidget( trailing_edge.get_widget() )

    def add_spar(self, xml_node=None):
        spar = Spar()
        spar.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            spar.parse_xml(xml_node)
        self.spars.append(spar)
        self.layout_spars.addWidget( spar.get_widget() )

    def add_stringer(self, xml_node=None):
        stringer = Spar()
        stringer.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            stringer.parse_xml(xml_node)
        self.stringers.append(stringer)
        self.layout_stringers.addWidget( stringer.get_widget() )

    def add_sheet(self, xml_node=None):
        sheet = Sheet()
        sheet.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            sheet.parse_xml(xml_node)
        self.sheeting.append(sheet)
        self.layout_sheeting.addWidget( sheet.get_widget() )

    def add_simple_hole(self, xml_node=None):
        hole = SimpleHole()
        hole.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            hole.parse_xml(xml_node)
        self.simple_holes.append(hole)
        self.layout_simple_holes.addWidget( hole.get_widget() )

    def add_shaped_hole(self, xml_node=None):
        hole = ShapedHole()
        hole.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            hole.parse_xml(xml_node)
        self.shaped_holes.append(hole)
        self.layout_shaped_holes.addWidget( hole.get_widget() )

    def add_build_tab(self, xml_node=None):
        tab = BuildTab()
        tab.rebuild_stations(self.edit_stations.text())
        if xml_node != None:
            tab.parse_xml(xml_node)
        self.build_tabs.append(tab)
        self.layout_build_tabs.addWidget( tab.get_widget() )

    def add_flap(self, xml_node=None):
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
        menu.addAction("Sheeting", self.add_sheet)
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
        for te_node in node.findall('trailing-edge'):
            self.add_trailing_edge(te_node)
        for spar_node in node.findall('spar'):
            self.add_spar(spar_node)
        for stringer_node in node.findall('stringer'):
            self.add_stringer(stringer_node)
        for sheet_node in node.findall('sheet'):
            self.add_sheet(sheet_node)
        for hole_node in node.findall('simple-hole'):
            self.add_simple_hole(hole_node)
        for hole_node in node.findall('shaped-hole'):
            self.add_shaped_hole(hole_node)
        for tab_node in node.findall('build-tab'):
            self.add_build_tab(tab_node)

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
        for te in self.trailing_edges:
            if te.valid:
                subnode = ET.SubElement(node, 'trailing-edge')
                te.gen_xml(subnode)
        for spar in self.spars:
            if spar.valid:
                subnode = ET.SubElement(node, 'spar')
                spar.gen_xml(subnode)
        for stringer in self.stringers:
            if stringer.valid:
                subnode = ET.SubElement(node, 'stringer')
                stringer.gen_xml(subnode)
        for sheet in self.sheeting:
            if sheet.valid:
                subnode = ET.SubElement(node, 'sheet')
                sheet.gen_xml(subnode)
        for hole in self.simple_holes:
            if hole.valid:
                subnode = ET.SubElement(node, 'simple-hole')
                hole.gen_xml(subnode)
        for hole in self.shaped_holes:
            if hole.valid:
                subnode = ET.SubElement(node, 'shaped-hole')
                hole.gen_xml(subnode)
        for tab in self.build_tabs:
            if tab.valid:
                subnode = ET.SubElement(node, 'build-tab')
                tab.gen_xml(subnode)



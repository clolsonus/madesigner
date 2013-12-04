#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Overview tab

author: Curtis L. Olson
website: madesigner.flightgear.org
started: November 2013
"""

import sys
from PyQt4 import QtGui, QtCore
import xml.etree.ElementTree as ET
from combobox_nowheel import QComboBoxNoWheel


class Overview():
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
        self.edit_desc = QtGui.QTextEdit()
        self.edit_desc.setFixedWidth(250)
        self.edit_desc.textChanged.connect(self.onChange)
        self.edit_author = QtGui.QLineEdit()
        self.edit_author.setFixedWidth(250)
        self.edit_author.textChanged.connect(self.onChange)
        self.edit_email = QtGui.QLineEdit()
        self.edit_email.setFixedWidth(250)
        self.edit_email.textChanged.connect(self.onChange)
        self.edit_units = QComboBoxNoWheel()
        self.edit_units.setFixedWidth(250)
        self.edit_units.addItem("in")
        self.edit_units.addItem("cm")
        self.edit_units.addItem("mm")

        layout.addRow( "<b>Design Name:</b>", self.edit_name )
        layout.addRow( "<b>Description:</b>", self.edit_desc )
        layout.addRow( "<b>Author:</b>", self.edit_author )
        layout.addRow( "<b>Email:</b>", self.edit_email )
        layout.addRow( "<b>Units:</b>", self.edit_units )

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
        self.edit_name.setText(self.get_value('name'))
        self.edit_desc.setText(self.get_value('description'))
        self.edit_author.setText(self.get_value('author'))
        self.edit_email.setText(self.get_value('email'))
        index = self.edit_units.findText(self.get_value('units'))
        if index == None:
            index = 1
        self.edit_units.setCurrentIndex(index)

    def update_node(self, node, value):
        e = self.xml.find(node)
        if e == None:
            e = ET.SubElement(self.xml, node)
        e.text = str(value)
        
    def gen_xml(self, node):
        self.xml = node
        self.update_node('name', self.edit_name.text())
        self.update_node('description', self.edit_desc.toPlainText())
        self.update_node('author', self.edit_author.text())
        self.update_node('email', self.edit_email.text())
        self.update_node('units', self.edit_units.currentText())

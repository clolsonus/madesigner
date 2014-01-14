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
#import xml.etree.ElementTree as ET
import lxml.etree as ET
from combobox_nowheel import QComboBoxNoWheel
from version import MADversion

class Overview():
    def __init__(self, changefunc):
        self.changefunc = changefunc
        self.container = self.make_page()
        self.xml = None
        self.version = MADversion()

    def onChange(self):
        self.changefunc()

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
        self.edit_units.currentIndexChanged.connect(self.onChange)
        self.edit_sheet_w = QtGui.QLineEdit()
        self.edit_sheet_w.setFixedWidth(250)
        self.edit_sheet_w.textChanged.connect(self.onChange)
        self.edit_sheet_h = QtGui.QLineEdit()
        self.edit_sheet_h.setFixedWidth(250)
        self.edit_sheet_h.textChanged.connect(self.onChange)

        layout.addRow( "<b>Design Name:</b>", self.edit_name )
        layout.addRow( "<b>Description:</b>", self.edit_desc )
        layout.addRow( "<b>Author:</b>", self.edit_author )
        layout.addRow( "<b>Email:</b>", self.edit_email )
        layout.addRow( "<b>Units:</b>", self.edit_units )
        layout.addRow( "<b>Mat. Sheet Width:</b>", self.edit_sheet_w )
        layout.addRow( "<b>Mat. Sheet Height:</b>", self.edit_sheet_h )

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
        units = self.get_value('units')
        sheet_w = self.get_value('sheet-width')
        sheet_h = self.get_value('sheet-height')
        if units == "in":
            if sheet_w == "":
                sheet_w = "24"
            if sheet_h == "":
                sheet_h = "12"
        elif units == "mm":
            if sheet_w == "":
                sheet_w = "600"
            if sheet_h == "":
                sheet_h = "300"
        elif units == "cm":
            if sheet_w == "":
                sheet_w = "60"
            if sheet_h == "":
                sheet_h = "30"
        index = self.edit_units.findText(units)
        if index == None:
            index = 0
        self.edit_units.setCurrentIndex(index)
        self.edit_sheet_w.setText(sheet_w)
        self.edit_sheet_h.setText(sheet_h)
        
        writer_version = self.get_value('MADversion')
        if writer_version == "" or float(writer_version) != self.version.get():
            if writer_version == "":
                writer_version = "(unknown)"
            reply = QtGui.QMessageBox.question(None, 'Version Alert', 'The design you are loading was created with MAD v' + str(writer_version) + '.  You are running v' + str(self.version.get()) + '.  The file will be converted as best as possible, but please check your design carefully for any issues.', QtGui.QMessageBox.Ok)

    def wipe_clean(self):
        self.edit_name.setText('')
        self.edit_desc.setText('')
        self.edit_author.setText('')
        self.edit_email.setText('')
        self.edit_units.setCurrentIndex(0)
        self.edit_sheet_w.setText('')
        self.edit_sheet_h.setText('')

    def update_node(self, node, value):
        e = self.xml.find(node)
        if e == None:
            e = ET.SubElement(self.xml, node)
        e.text = str(value)
        
    def gen_xml(self, node):
        self.xml = node
        self.update_node('MADversion', str(self.version.get()))
        self.update_node('name', self.edit_name.text())
        self.update_node('description', self.edit_desc.toPlainText())
        self.update_node('author', self.edit_author.text())
        self.update_node('email', self.edit_email.text())
        self.update_node('units', self.edit_units.currentText())
        self.update_node('sheet-width', self.edit_sheet_w.text())
        self.update_node('sheet-height', self.edit_sheet_h.text())

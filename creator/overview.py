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

from props import root, getNode

from combobox_nowheel import QComboBoxNoWheel
from version import MADversion

class Overview():
    def __init__(self, changefunc):
        self.changefunc = changefunc
        self.container = self.make_page()
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
        self.edit_plans_w = QtGui.QLineEdit()
        self.edit_plans_w.setFixedWidth(250)
        self.edit_plans_w.textChanged.connect(self.onChange)
        self.edit_plans_h = QtGui.QLineEdit()
        self.edit_plans_h.setFixedWidth(250)
        self.edit_plans_h.textChanged.connect(self.onChange)

        layout.addRow( "<b>Design Name:</b>", self.edit_name )
        layout.addRow( "<b>Description:</b>", self.edit_desc )
        layout.addRow( "<b>Author:</b>", self.edit_author )
        layout.addRow( "<b>Email:</b>", self.edit_email )
        layout.addRow( "<b>Units:</b>", self.edit_units )
        layout.addRow( "<b>Mat. Sheet Width:</b>", self.edit_sheet_w )
        layout.addRow( "<b>Mat. Sheet Height:</b>", self.edit_sheet_h )
        layout.addRow( "<b>Plans Width:</b>", self.edit_plans_w )
        layout.addRow( "<b>Plans Height:</b>", self.edit_plans_h )

        return page

    def get_widget(self):
        return self.container

    def load(self, node):
        self.edit_name.setText(node.getString('name'))
        self.edit_desc.setText(node.getString('description'))
        self.edit_author.setText(node.getString('author'))
        self.edit_email.setText(node.getString('email'))
        units = node.getString('units')
        sheet_w = node.getString('sheet_width')
        sheet_h = node.getString('sheet_height')
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
        plans_w = node.getString('plans_width')
        plans_h = node.getString('plans_height')
        if units == "in":
            if plans_w == "":
                plans_w = "24"
            if plans_h == "":
                plans_h = "36"
        elif units == "mm":
            if plans_w == "":
                plans_w = "600"
            if plans_h == "":
                plans_h = "900"
        elif units == "cm":
            if plans_w == "":
                plans_w = "60"
            if plans_h == "":
                plans_h = "90"
        index = self.edit_units.findText(units)
        if index == None:
            index = 0
        self.edit_units.setCurrentIndex(index)
        self.edit_sheet_w.setText(sheet_w)
        self.edit_sheet_h.setText(sheet_h)
        self.edit_plans_w.setText(plans_w)
        self.edit_plans_h.setText(plans_h)
        
        writer_version = node.getString('MADversion')
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
        self.edit_sheet_w.setText('24')
        self.edit_sheet_h.setText('12')
        self.edit_plans_w.setText('24')
        self.edit_plans_h.setText('36')

    def save(self, node):
        node.setString('MADversion', str(self.version.get()))
        node.setString('name', self.edit_name.text())
        node.setString('description', self.edit_desc.toPlainText())
        node.setString('author', self.edit_author.text())
        node.setString('email', self.edit_email.text())
        node.setString('units', self.edit_units.currentText())
        node.setString('sheet_width', self.edit_sheet_w.text())
        node.setString('sheet_height', self.edit_sheet_h.text())
        node.setString('plans_width', self.edit_plans_w.text())
        node.setString('plans_height', self.edit_plans_h.text())

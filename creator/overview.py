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


class Overview():
    def __init__(self):
        self.name = ""
        self.description = ""
        self.author = ""
        self.email = ""
        self.container = self.make_page()
        self.xml = None

    def onChange(self):
        self.name = self.edit_name.text();
        self.description = self.edit_desc.toPlainText();
        self.author = self.edit_author.text();
        self.email = self.edit_email.text();

    def make_page(self):
        # make the full edit widget
        page = QtGui.QFrame()
        layout = QtGui.QGridLayout()
        page.setLayout( layout )

        label1 = QtGui.QLabel( "<b>Design Name:</b>" )
        label2 = QtGui.QLabel( "<b>Description:</b>" )
        label3 = QtGui.QLabel( "<b>Author Name:</b>" )
        label4 = QtGui.QLabel( "<b>Email:</b>" )

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

        layout.addWidget( label1, 0, 0, QtCore.Qt.AlignRight )
        layout.addWidget( label2, 1, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop )
        layout.addWidget( label3, 2, 0, QtCore.Qt.AlignRight )
        layout.addWidget( label4, 3, 0, QtCore.Qt.AlignRight )

        layout.addWidget( self.edit_name, 0, 1, QtCore.Qt.AlignLeft )
        layout.addWidget( self.edit_desc, 1, 1, QtCore.Qt.AlignLeft )
        layout.addWidget( self.edit_author, 2, 1, QtCore.Qt.AlignLeft )
        layout.addWidget( self.edit_email, 3, 1, QtCore.Qt.AlignLeft )

        return page

    def widget(self):
        return self.container

    def get_value(self, node):
        e = self.xml.find(node)
        if e != None:
            return e.text
        else:
            return ""

    def parse_xml(self, node):
        self.xml = node

        self.name = self.get_value('name')
        self.edit_name.setText(self.name)

        self.description = self.get_value('description')
        self.edit_desc.setText(self.description)

        self.author = self.get_value('author')
        self.edit_author.setText(self.author)

        self.email = self.get_value('email')
        self.edit_email.setText(self.email)

    def update_node(self, node, value):
        e = self.xml.find(node)
        if e == None:
            e = ET.SubElement(self.xml, node)
        e.text = str(value)
        
    def gen_xml(self, node):
        self.xml = node

        self.update_node('name', self.name)
        self.update_node('description', self.description)
        self.update_node('author', self.author)
        self.update_node('email', self.email)


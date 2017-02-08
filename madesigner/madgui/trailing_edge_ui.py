# trailing_edge_ui.py - trailing edge user interface components
#
# Copyright (C) 2013-2017 - Curtis Olson, curtolson@flightgear.org
# http://madesigner.flightgear.org

import sys

from PyQt5.QtWidgets import (QWidget,
                             QHBoxLayout, QVBoxLayout, QFrame, QFormLayout,
                             QPushButton, QTabWidget, QGroupBox,
                             QLineEdit, QTextEdit, QLabel, QScrollArea,
                             QInputDialog, QMenu)

from combobox_nowheel import QComboBoxNoWheel


class TrailingEdgeUI():
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
        # make the edit line
        page = QFrame()
        layout = QVBoxLayout()
        page.setLayout( layout )

        line1 = QFrame()
        layout1 = QHBoxLayout()
        line1.setLayout( layout1 )
        layout.addWidget( line1 )

        layout1.addWidget( QLabel("<b>W x H:</b> ") )

        self.edit_width = QLineEdit()
        self.edit_width.setFixedWidth(50)
        self.edit_width.textChanged.connect(self.onChange)
        layout1.addWidget( self.edit_width )

        self.edit_height = QLineEdit()
        self.edit_height.setFixedWidth(50)
        self.edit_height.textChanged.connect(self.onChange)
        layout1.addWidget( self.edit_height )

        self.edit_shape = QComboBoxNoWheel()
        self.edit_shape.addItem("Flat Triangle")
        self.edit_shape.addItem("Symmetrical") 
        self.edit_shape.addItem("Bottom Sheet")
        self.edit_shape.currentIndexChanged.connect(self.onChange)
        layout1.addWidget(self.edit_shape)

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

        delete = QPushButton('Delete ')
        delete.clicked.connect(self.delete_self)
        layout1.addWidget(delete)

        return page

    def get_widget(self):
        return self.container

    def load(self, node):
        self.edit_width.setText(node.getString('width'))
        self.edit_height.setText(node.getString('height'))
        index = self.edit_shape.findText(node.getString('shape'))
        if index == None:
            index = 1
        self.edit_shape.setCurrentIndex(index)
        index = self.edit_start.findText(node.getString('start_station'))
        if index != None:
            self.edit_start.setCurrentIndex(index)
        index = self.edit_end.findText(node.getString('end_station'))
        if index != None:
            self.edit_end.setCurrentIndex(index)

    def save(self, node):
        node.setString('width', self.edit_width.text())
        node.setString('height', self.edit_height.text())
        node.setString('shape', self.edit_shape.currentText())
        node.setString('start_station', self.edit_start.currentText())
        node.setString('end_station', self.edit_end.currentText())

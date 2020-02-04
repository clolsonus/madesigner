# flap_ui.py - flap user interface components
#
# Copyright (C) 2013-2017 - Curtis Olson, curtolson@flightgear.org
# http://madesigner.flightgear.org

import sys

from PyQt5.QtWidgets import (QWidget,
                             QHBoxLayout, QVBoxLayout, QFrame, QFormLayout,
                             QPushButton, QTabWidget, QGroupBox,
                             QLineEdit, QTextEdit, QLabel, QScrollArea,
                             QInputDialog, QMenu)

from .combobox_nowheel import QComboBoxNoWheel


class FlapUI():
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
        page = QFrame()
        layout = QVBoxLayout()
        page.setLayout( layout )

        line1 = QFrame()
        layout1 = QHBoxLayout()
        line1.setLayout( layout1 )
        layout.addWidget( line1 )

        line2 = QFrame()
        layout2 = QHBoxLayout()
        line2.setLayout( layout2 )
        layout.addWidget( line2 )

        line3 = QFrame()
        layout3 = QHBoxLayout()
        line3.setLayout( layout3 )
        layout.addWidget( line3 )

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

        delete = QPushButton('Delete')
        delete.clicked.connect(self.delete_self)
        layout1.addWidget(delete)
  
        layout2.addWidget( QLabel("<b>Pos:</b> ") )

        self.edit_posref = QComboBoxNoWheel()
        self.edit_posref.addItem("Chord %")
        self.edit_posref.addItem("Rel Front")
        self.edit_posref.addItem("Rel Rear")
        self.edit_posref.addItem("Abs Pos")
        self.edit_posref.currentIndexChanged.connect(self.onChange)
        layout2.addWidget(self.edit_posref)

        self.edit_pos = QLineEdit()
        self.edit_pos.setFixedWidth(50)
        self.edit_pos.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_pos )

        layout2.addWidget( QLabel("<b>At Station:</b> ") )
        self.edit_atstation = QLineEdit()
        self.edit_atstation.setFixedWidth(50)
        self.edit_atstation.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_atstation )

        layout2.addWidget( QLabel("<b>Slope:</b> ") )
        self.edit_slope = QLineEdit()
        self.edit_slope.setFixedWidth(50)
        self.edit_slope.textChanged.connect(self.onChange)
        layout2.addWidget( self.edit_slope )

        layout2.addStretch(1)

        layout3.addWidget( QLabel("<b>Edge Stringer W x H:</b> ") )

        self.edit_width = QLineEdit()
        self.edit_width.setFixedWidth(50)
        self.edit_width.textChanged.connect(self.onChange)
        layout3.addWidget( self.edit_width )

        self.edit_height = QLineEdit()
        self.edit_height.setFixedWidth(50)
        self.edit_height.textChanged.connect(self.onChange)
        layout3.addWidget( self.edit_height )

        layout3.addWidget( QLabel("<b>Hinge Cutout Angle:</b> ") )

        self.edit_angle = QLineEdit()
        self.edit_angle.setFixedWidth(50)
        self.edit_angle.textChanged.connect(self.onChange)
        layout3.addWidget( self.edit_angle )

        layout3.addStretch(1)

        return page

    def get_widget(self):
        return self.container

    def load(self, node):
        self.edit_width.setText(node.getString('width'))
        self.edit_height.setText(node.getString('height'))
        index = self.edit_posref.findText(node.getString('position_ref'))
        if index == None:
            index = 1
        self.edit_posref.setCurrentIndex(index)
        self.edit_pos.setText(node.getString('position'))
        self.edit_atstation.setText(node.getString('at_station'))
        self.edit_slope.setText(node.getString('slope'))
        self.edit_angle.setText(node.getString('angle'))
        index = self.edit_start.findText(node.getString('start_station'))
        if index != None:
            self.edit_start.setCurrentIndex(index)
        index = self.edit_end.findText(node.getString('end_station'))
        if index != None:
            self.edit_end.setCurrentIndex(index)

    def save(self, node):
        node.setString('width', self.edit_width.text())
        node.setString('height', self.edit_height.text())
        node.setString('position_ref', self.edit_posref.currentText())
        node.setString('position', self.edit_pos.text())
        node.setString('at_station', self.edit_atstation.text())
        node.setString('slope', self.edit_slope.text())
        node.setString('angle', self.edit_angle.text())
        node.setString('start_station', self.edit_start.currentText())
        node.setString('end_station', self.edit_end.currentText())

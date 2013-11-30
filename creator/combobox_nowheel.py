#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Combo box that ignores scroll wheel input

Reference: http://nathanhorne.com/?p=254

author: Curtis L. Olson
website: madesigner.flightgear.org
started: November 2013
"""

from PyQt4 import QtGui, QtCore

class QComboBoxNoWheel(QtGui.QComboBox):
    def wheelEvent (self, event):
        event.ignore()

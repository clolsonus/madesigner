# combobox_nowheel.py - Combo box that ignores scroll wheel input
#
# Copyright (C) 2013-2017 - Curtis Olson, curtolson@flightgear.org
# http://madesigner.flightgear.org
#
# Reference: http://nathanhorne.com/?p=254

from PyQt5.QtWidgets import QComboBox

class QComboBoxNoWheel(QComboBox):
    def wheelEvent (self, event):
        event.ignore()

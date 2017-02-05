#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
MA creator 

This program hopefully does something eventually ...

author: Curtis L. Olson
website: madesigner.flightgear.org
started edited: November 2013
"""

import os.path
import sys
from PyQt4 import QtGui, QtCore
from creator.creator_ui import CreatorUI

def usage():
    print "Usage: " + sys.argv[0] + " [design.mad]"

def main():
    app = QtGui.QApplication(sys.argv)
    filename = ""
    if len(sys.argv) > 2:
        usage()
        return
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
    ex = CreatorUI(filename)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

#!/usr/bin/python

"""
MAdesigner - Model Airplane Rapid Design Toolkit

Copyright (C) 2013-2017 - Curtis Olson, curtolson@flightgear.org
http://madesigner.flightgear.org

"""

import os.path
import sys
from PyQt5.QtWidgets import QApplication
from madgui.creator_ui import CreatorUI

def usage():
    print "Usage: " + sys.argv[0] + " [design.mad]"

def main():
    app = QApplication(sys.argv)
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

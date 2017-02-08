# version.py - build it!
#
# Copyright (C) 2013-2017 - Curtis Olson, curtolson@flightgear.org
# http://madesigner.flightgear.org

# official program version stored here

class MADversion():
    def __init__(self):
        self.version = 2.0

    def get(self):
        return self.version

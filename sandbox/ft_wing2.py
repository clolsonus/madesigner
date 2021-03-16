#!/usr/bin/env python3

# this is a quick test to compute dimensions for a flight test style
# folded foam board wing ... losely based on the clarky airfoil sorta
# kinda

import argparse
import math
import matplotlib.pyplot as plt
import numpy as np

from ft_profile import FtProfile

ap = argparse.ArgumentParser(description="Compute the dimensions of FT-style folded wing.  All dimensions are mm unless otherwise noted.")
ap.add_argument('chord_mm', type=int, nargs="+", help='desired chord')
ap.add_argument('--material_mm', type=float, default=4.9,
                help='material thickness')
args = ap.parse_args()

# units: let's do mm
r2d = 180 / math.pi

af_list = []
for chord_mm in args.chord_mm:
    af = FtProfile(chord_mm, args.material_mm)
    af.compute()
    af.plot()
    af_list.append(af)

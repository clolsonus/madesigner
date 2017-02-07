#!/usr/bin/env python

from setuptools import setup, find_packages

#print find_packages('madesigner')

setup( name = 'madesigner',
       version = '2.0',
       description = 'Model airplane design toolkit.',
       author = 'Curtis L. Olson',
       author_email = 'curtolson@flightgear.org',
       url = 'http://madesigner.flightgear.org',
       license = "GPLv3",
       package_dir = {'': 'madesigner'},
       packages = find_packages('madesigner'),
       scripts = [ 'madesigner/madesigner.py' ],
       package_data = { 'madlib': ['airfoils/*.dat'] },
       install_requires = ['svgwrite', 'Polygon2'],
       )


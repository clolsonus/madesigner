#!/usr/bin/env python

from setuptools import setup, find_packages

print find_packages()

setup( name = 'madesigner',
       version = '2.0',
       description = 'Model airplane design toolkit.',
       author = 'Curtis L. Olson',
       author_email = 'curtolson@flightgear.org',
       url = 'http://madesigner.flightgear.org',
       # package_dir = {'': 'madesigner'},
       # packages = [ 'lib' ],
       packages = [ 'madesigner', 'madesigner.creator', 'madesigner.lib' ],
       #scripts = [ 'madesigner/creator.py' ],
       #package_data = {'madesigner': ['airfoils/*.dat']},
       )


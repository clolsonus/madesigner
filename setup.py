#!/usr/bin/env python

from distutils.core import setup

setup( name = 'madesigner',
       version = '2.0',
       description = 'Model airplane design tool.',
       author = 'Curtis L. Olson',
       author_email = 'curtolson@flightgear.org',
       url = 'http://madesigner.flightgear.org',
       # package_dir = {'': 'src'},
       # packages = [ 'lib' ],
       packages = [ 'madesigner', 'madesigner.creator', 'madesigner.lib' ]
       # scripts = [ 'src/madesigner/creator.py' ],
       # package_data = {'madesigner': ['data/airfoils/*.dat']},
       )

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup

setup(
    name='pick',
    version='1.0',

    url='https://kryogenix.org/code/pick',

    author='Stuart Langridge',
    author_email='sil@kryogenix.org',

    packages=['pick'],
    package_dir={'pick': 'pick'},

    data_files=[
        (sys.prefix+'/share/applications',['pick.desktop']),
        (sys.prefix+'/share/pixmaps', ['pick.png'])
    ],

    zip_safe=True,
    include_package_data=True,

    platforms='any',

    install_requires=[
        'PyGObject',
        'setuptools'
    ],

    description='A colour picker that remembers where you picked colours from',
    long_description=("Pick lets you pick colours from anywhere on your screen. "
        "Choose the colour you want and Pick remembers it, names it, and shows you a screenshot "
        "so you can remember where you got it from. Zoom all the way in to pixels to pick "
        "just the right one. Show your colours in your choice of format: rgba() or hex, "
        "CSS or Gdk or Qt, whichever you prefer. Copy to the clipboard ready for pasting into "
        "code or graphics apps."),

    keywords=['pick', 'colour', 'colour picker', 'color', 'color picker'],

    license='MIT',
    classifiers=[
        'Programming Language :: Python',
        'Environment :: X11 Applications :: GTK',
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Multimedia :: Graphics'
    ],

    entry_points={
        'gui_scripts': [
            'pick = pick.__main__:main',
        ]
    },
)

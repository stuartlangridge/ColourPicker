#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='pick',
    version='1.0',

    url='https://kryogenix.org/code/pick',

    author='Stuart Langridge',
    author_email='sil@kryogenix.org',

    packages=[],
    package_dir={},
    package_data={},

    zip_safe=True,
    include_package_data=True,

    platforms='any',

    install_requires=[
        'PyGObject',
        'setuptools'
    ],

    description='A colour picker for Ubuntu and elementary',
    long_description=open('../README.md', 'r').read(),

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
)

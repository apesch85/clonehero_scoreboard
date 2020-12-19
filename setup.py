#! /usr/bin/python3

from setuptools import setup
from setuptools import dist
dist.Distribution().fetch_build_eggs(['Cython', 'numpy>=1.18.5'])

setup(
    setup_requires=[
      # Setuptools 18.0 properly handles Cython extensions.
      'cython',
    ],
   name='clonehero_scoreboard',
   version='0.5',
   description='A tool for tracking Clonehero scores',
   author='apesch85',
   packages=['clonehero_scoreboard_app'],
   install_requires=[
     'cycler',
     'decorator',
     'future',
     'gspread==3.6.0',
     'imageio',
     'kiwisolver==1.1.0',
     'matplotlib',
     'networkx',
     'Pillow>=8.0'
     'pkg-resources',
     'pyparsing',
     'pytesseract==0.3.6',
     'python-dateutil',
     'PyWavelets',
     'six',
     'absl-py'
   ]
)

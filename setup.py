#! /usr/bin/python3

from setuptools import setup

setup(
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
     'matplotlib==3.0.3',
     'networkx',
     'numpy==1.18.5',
     'Pillow==7.2.0',
     'pkg-resources',
     'pyparsing',
     'pytesseract==0.3.6',
     'python-dateutil',
     'PyWavelets',
     'six',
     'absl-py'
   ]
)

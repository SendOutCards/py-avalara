#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages
import sys

requirements = [
    "requests",
    "serpy",
    "six",
]

setup_requires = []
if 'test' in sys.argv:
    setup_requires.append('pytest-runner')

tests_require = [
    'pytest',
]

version = '0.1.2'

setup(
    name='avalara',
    version=version,
    description='Python client to interact Avalara',
    author='SendOutCards',
    packages=find_packages(exclude=['*.tests']),
    zip_safe=False,
    install_requires=requirements,
    tests_require=tests_require,
    setup_requires=setup_requires,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Private :: Do Not Upload"
    ],
)

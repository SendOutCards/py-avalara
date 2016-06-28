#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

requirements = [
    "requests",
    "six",
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
    classifier=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Private :: Do Not Upload"
    ],
)

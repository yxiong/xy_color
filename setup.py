#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Apr 23, 2015.

from setuptools import setup

install_requires = [
    "matplotlib",
    "numpy",
    "numpydoc",
    "Pillow",
    "scipy",
    "setuptools",
    "Sphinx==1.2.3",
    "tornado",
]

setup(
    name = "xy_color",
    version = "0.1.dev",
    url = "https://github.com/yxiong/xy_color",
    author = "Ying Xiong",
    author_email = "yxiong@seas.harvard.edu",
    description = "Utilities and demos for color science in Python.",
    packages = ["xy_color",],
    install_requires = install_requires
)

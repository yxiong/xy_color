#!/usr/bin/env python
#
# Author: Ying Xiong.
# Created: Apr 23, 2015.

from setuptools import setup

with open("requirements.txt", 'r') as f:
    install_requires = f.read().splitlines()

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

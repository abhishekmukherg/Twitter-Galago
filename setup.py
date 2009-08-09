#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="twitter_galago",
        version="1.0",
        description="Twitter client that just pops up galago notifications, nothing else",
        author="Abhishek Mukherjee",
        author_email="abhishek.mukher.g@gmail.com",
        packages = find_packages(),
        zip_safe = True)


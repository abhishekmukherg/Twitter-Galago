#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="oauthtwitter",
        version="1.0",
        description="Library for OAuth Twitter",
        author="Hameed Khan",
        author_email="leah.culver@gmail.com",
        url="http://code.google.com/p/oauth-python-twitter",
        packages = find_packages(),
        zip_safe = True)


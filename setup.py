#!/usr/bin/env python

"""
distutils/setuptools install script.
"""

import os
import sys
import kotocore

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup


packages = [
    'kotocore',
    'kotocore.utils',
]

requires = [
    'botocore>=0.24.0',
    'six>=1.4.0',
    'jmespath>=0.1.0',
    'python-dateutil>=2.1',
]

setup(
    name='kotocore',
    version=kotocore.get_version(),
    description='Utility for botocore.',
    long_description=open('README.rst').read(),
    author='Henry Huang',
    author_email='henry.s.huang@gmail.com',
    url='https://github.com/henrysher/kotocore',
    scripts=[],
    packages=packages,
    package_data={
        'kotocore': [
            'data/aws/resources/*.json',
        ]
    },
    include_package_data=True,
    install_requires=requires,
    license=open("LICENSE").read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)

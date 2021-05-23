#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The setup script."""

import sys
from setuptools import setup, find_packages

sys.path[0:0] = ['kafkacli']
from version import __version__


setup(
    name='kafkacli',
    include_package_data=True,
    packages=find_packages(include=['kafkacli']),
    version=__version__,
    description="An advanced Kafka client",
    entry_points={ 'console_scripts': [ 'kafkacli=kafkacli.main:main' ],},
    install_requires=['requests','pygments','avro-python3','kafka-python'],
    setup_requires=['pytest-runner','pycodestyle'],
    tests_require=['pytest'],
    test_suite='tests',
    zip_safe=False
)

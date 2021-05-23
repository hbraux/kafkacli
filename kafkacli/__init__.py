#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__title__ = 'kafkacli'
from .version import __version__

from kafkacli.client import Client
__all__ = ['Client']

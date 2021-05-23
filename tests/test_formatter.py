#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import json
from kafkacli.formatter import Formatter

sampleJson = json.loads('{"a":"s", "b":1}')


def test_print_default(capsys):
    Formatter().print(sampleJson)
    captured = capsys.readouterr()
    assert captured.out == '{"a": "s", "b": 1}\n'


def test_print_idents(capsys):
    Formatter(indents=True).print(sampleJson)
    captured = capsys.readouterr()
    assert captured.out == '{\n    "a": "s",\n    "b": 1\n}\n'


def test_print_colors(capsys):
    Formatter(colors=True).print(sampleJson)
    captured = capsys.readouterr()
    assert captured.out == \
        '{"a": \x1b[34m"s"\x1b[39m, "b": \x1b[31m1\x1b[39m}\n'

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unit Tests are using a docker Kafla cluster
# TODO: migrate to mock and fixtures
# Example: https://github.com/dpkp/kafka-python/blob/master/test/conftest.py

"""Tests for `kafkacli` package."""

import os
import pytest
import socket
from kafkacli import Client
from datetime import datetime, timedelta

BROKER = socket.gethostname() + ':9092'
REGISTRY = 'http://localhost:8081'
TOPIC = os.getenv("TEST_TOPIC", "test")
SCHEMA_FILE = "tests/sample.asvc"
SEED = 1


def test_topics():
    client = Client(BROKER, TOPIC)
    assert client.open()
    assert '_schemas' in client.get_topics(showall=True)
    # assert TOPIC in client.get_topics()


def test_schemas():
    client = Client(BROKER, TOPIC, REGISTRY)
    assert client.open()
    assert client.register_schema(open(SCHEMA_FILE, 'r'))
    scheme = open(SCHEMA_FILE, 'r').read().replace('\n', '').replace(' ', '')
    assert client.get_schema() == scheme


def test_generate():
    client = Client(BROKER, TOPIC, REGISTRY)
    assert client.open()
    assert client.generate('{"int":"%INT99999"}', 0, SEED, 1, True) == \
        {'int': '17611'}
    assert client.generate('{"str":"%STR10"}', 0, SEED, 1, True) == \
        {'str': 'DWTGMLQUCA'}
    assert client.generate('{"uuid":"%UUID"}', 0, SEED, 1, True) == \
        {'uuid': 'cd613e30-d8f1-6adf-91b7-584a2265b1f5'}
    assert client.generate('{"id":"%ID5"}', 0, SEED, 1, True) == \
        {'id': 'eszyc'}
    assert client.generate('{"dt":"%DATE0"}', 0, SEED, 1, True) == \
        {'dt': datetime.now().isoformat()[0:10]}
    assert client.generate('{"dt":"%DATE1"}', 0, SEED, 1, True) == \
        {'dt': (datetime.now()+timedelta(days=-1)).isoformat()[0:10]}
    assert client.generate('{"dt":"%TIME0"}', 0, SEED, 1, True) == \
        {'dt': datetime.now().isoformat()[0:19]}
    assert client.generate('{"dt":"%TIME86400"}', 0, SEED, 1, True) == \
        {'dt': (datetime.now()+timedelta(days=-1)).isoformat()[0:19]}

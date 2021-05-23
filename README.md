======
kafkacli
======

|badge1| |badge2|

.. |badge1| image:: https://github.com/hbraux/kafkacli/workflows/build/badge.svg
:alt: Build status
:target: https://github.com/hbraux/pysds/actions

.. |badge2| image:: https://raw.githubusercontent.com/hbraux/kafkacli/master/coverage.svg
:alt: Coverage


An advanced Kaka Client command line interface (written in Python)


## Overview

**kafkacli** is an alternative to the legacy kafka-console-consumer

It supports JSON and AVRO messages (assuming a Schema Registry is running) and provides a random messages generator

## Usage

It is recommended to use the Docker image which does not require any pre-requisites (except Docker)

```
docker run -it --rm -e KAFKA_SERVER=myconfluentserver docker.pkg.github.com/kafkacli ARGS...
```

## Python Package

### History

* Version 0.1.3 is now stable

### Installation

Prerequisites: Python 3.6 or higher

```
pip3 install git+https://gitlab.com/haroldbraux/kafkacli.git
```

### Command Line

Run script without arguments to get help
```
usage: kafkacli [-h] [-D] [--version]
                {list,show,register,print,join,count,extract,generate,avro}
                ...

optional arguments:
  -h, --help            show this help message and exit
  -D, --debug
  --version             show program's version number and exit

subcommands:
  {list,show,register,print,join,count,extract,generate,avro}
    list                list topics
    show                show topic schema
    register            register a chema
    print               print topic to stdout
    join                join topics and get measures
    count               count messages in a topic
    extract             extract topic data and get measures
    generate            message generator
    avro                Avro file utility

```



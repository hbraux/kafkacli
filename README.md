# kafkacli

An advanced command line interface for Kafka written in Python.

Alternative to the legacy kafka-console-consumer/producer  
Supports JSON and AVRO messages (assuming a Schema Registry is running)  
Includes a random messages generator

## Status

* Version 0.1.3 is now stable

## Install

Prerequisites: Python 3.6 or higher

```
pip3 install git+https://gitlab.com/haroldbraux/kafkacli.git
```

## Usage

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

## Docker Usage

```
docker run -it --rm -e SITE_KAFKA=myconfluentserver haroldbraux/kafkacli ARGS...
```


## Still TODO
* More unit tests

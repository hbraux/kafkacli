# kafkacli

![Test status](https://github.com/hbraux/kafkacli/workflows/build/badge.svg)
![Coverage](https://raw.githubusercontent.com/hbraux/kafkacli/master/coverage.svg)

An advanced Kafka / Confluent client command line interface (written in Python)

## Features

* List topics
* Print topic content (behaves as a `kafka-console-consumer`)
* Decode Avro messages (assuming a Schema Registry is running)
* Pretty print Json/Avro messages (colors, indents)
* Write random JSON messages on a topic (testing purpose)
* Compute latencies on messages (basic support of Time Series)
* Decode Avro files
* Print and register a schema on the Registry

## Usage

It is recommended using the Docker image `hbraux/kafkacli` (available on [Docker Hub](https://hub.docker.com/)) as
it does not require any Python dependency.

The container expects either `KAFKA_SERVER`, or `KAFKA_BROKERS_LIST` and `KAFKA_REGISTRY_URL` to be set,
respectivly with the hostname of the Confluent Server, or the brokers hosts and ports and Schema Registry URL.

Examples:
```
docker run -it --rm --network host -e KAFKA_SERVER=mykafka hbraux/kafkacli print
```

* Option `--network host` should make the Container able to resolve hostnames. Otherwise use `--add-host mykafka:@IP` 

## Python Package


### Installation

Prerequisites:
* Python 3.6 or higher
* Python Packages in `requirements.txt`
* Optionally snappy-lib when kafka topics are compressed

```
pip3 install git+https://github.com/hbraux/kafkacli.git
```

### Command Line

Run script without any argument to get the general help and all available commands.

Run script with `COMMAND --help` to get the command options and arguments.

```
usage: kafkacli [-h] [-D] [--version]
                {list,show,register,print,join,count,extract,generate,avro}
                ...

optional arguments:
  -h, --help            show this help message and exit
  -D, --debug
  --version             show program's version number and exit

commands:
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

### History

* 0.1.4 (23/05/21) stable version 

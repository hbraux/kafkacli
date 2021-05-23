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

As for Docker, you can set the environment variables `KAFKA_SERVER`, or `KAFKA_BROKERS_LIST` and `KAFKA_REGISTRY_URL` 
if you don't want to provide them as command line options.

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

### Example

```shell
$ kafkacli list
testtopic
$ kafkacli  generate testtopic -n 10  '{"uuid":"%UUID","str":"%STR10","dt":"%DATE1"}'
$ kafkacli  print -p testtopic
{"uuid": "2d8af9a4-42a2-99c4-d265-3203a4647540", "str": "AXUTFBBELN", "dt": "2021-05-13"}
{"uuid": "f50942b5-0227-87d2-99be-190cc34b8a1e", "str": "TJPBPXJJUR", "dt": "2021-05-14"}
{"uuid": "b1e56025-6ca4-2764-289c-7c57a3eed777", "str": "HUBRYYLDZU", "dt": "2021-05-15"}
{"uuid": "0bacb398-0c20-7db5-6120-93c69f496d37", "str": "UWSPWYFVBT", "dt": "2021-05-16"}
{"uuid": "f60b23ed-3cba-ed4b-0448-42ed2a145a56", "str": "KFWTKVJRVG", "dt": "2021-05-17"}
{"uuid": "670d2dbd-49f3-488b-5746-e20ffa06a690", "str": "HDXPKNCFOH", "dt": "2021-05-18"}
{"uuid": "5a159295-8ac9-3689-1b65-baabc7dc71a6", "str": "RVCDHVHPQV", "dt": "2021-05-19"}
{"uuid": "50ba9f12-4b69-c9c9-d291-d5c5a887cdbb", "str": "UDFDXYXWPU", "dt": "2021-05-20"}
{"uuid": "7bdd6692-539c-d763-dd3e-8744565e6914", "str": "ALGCUIUIHW", "dt": "2021-05-21"}
{"uuid": "92b258cc-cd32-24dc-01f0-559b3addb03f", "str": "MHQEBGXRIX", "dt": "2021-05-22"}
```

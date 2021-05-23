# -*- coding: utf-8 -*-

"""Console script ."""

from __future__ import print_function
import sys
import os
import argparse
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    sys.stderr.write("Tool requires Python 3.6 or higher!\n")
    sys.exit(-1)
from kafkacli.client import Client  # nopep8
from kafkacli.avrofile import AvroFile  # nopep8
from kafkacli.formatter import Formatter  # nopep8
from kafkacli.__init__ import __version__  # nopep8


CRED = '\033[31m'
CEND = '\033[0m'

# If environment variables are set, use them as default broker/registry
KAFKA_SERVER = os.getenv('KAFKA_SERVER')
BROKER = os.getenv('KAFKA_BROKERS_LIST', KAFKA_SERVER + ':9092'
                   if KAFKA_SERVER else None)
REGISTRY = os.getenv('KAFKA_REGISTRY_URL', 'http://' + KAFKA_SERVER + ':8881'
                     if KAFKA_SERVER else None)
DEFAULT_KEY = 'Id'
HELP_BROKERS = "server:port,... (optional when $KAFKA_BROKERS_LIST or $KAFKA_SERVER is set)"  # nopep8
HELP_REGISTRY = "http://server:port (optional when $KAFKA_REGISTRY_URL or $KAFKA_SERVER is set)"  # nopep8


def die(*msg):
    sys.stderr.write(CRED)
    sys.stderr.write("Error: ")
    print(*msg, file=sys.stderr)
    sys.stderr.write(CEND)
    sys.exit(1)


def list_topics(brokers, registry, details, debug):
    client = Client(brokers, '_schemas', registry, debug=debug)
    if not client.open():
        die(client.get_error())
    for t in client.get_topics(details):
        if isinstance(t, list):
            print("\t".join(t))
        else:
            print(t)


def count_topic(brokers, topic, debug):
    client = Client(brokers, topic, debug=debug)
    if not client.open():
        die(client.get_error())
    client.read_topic()
    print(client.get_read())


def show_schema(brokers, topic, registry, sample, debug):
    client = Client(brokers, topic, registry, debug=debug)
    if not client.open():
        die(client.get_error())
    if sample:
        print(str(client.get_sample_record()).replace("'", '"'))
    else:
        print(client.get_schema())


def register_schema(brokers, topic, registry, schemafile, debug):
    client = Client(brokers, topic, registry, debug=debug)
    if not client.open() or not client.register_schema(schemafile):
        die(client.get_error())
    print("schema registered")


def print_topic(brokers, topic, registry, group, output, num, metadata,
                pretty, ppretty, filters, debug):
    client = Client(brokers, topic, registry, group, debug=debug)
    if not client.open():
        die(client.get_error())
    ffield = filters.split('=')[0] if (filters) else None
    fvalue = filters.split('=')[1] if (filters) else None
    client.print_topic(Formatter(pretty or ppretty, ppretty), output, num,
                       metadata, ffield, fvalue)
    client.close()


def msg_generator(brokers, topic, registry, delay, seed, num, message,
                  stdout, compress, debug):
    client = Client(brokers, topic, registry, debug=debug)
    if not client.open():
        die(client.get_error())
    client.generate(message, delay, seed, num, stdout, compress)


def join_topics(brokers, registry, topic, group, num, idfield, joined_topic,
                joined_idfield, debug):
    client = Client(brokers, topic, registry, group, field=idfield,
                    debug=debug)
    if not client.open():
        die(client.get_error())
    series = client.join(joined_topic, joined_idfield, num)
    if not series:
        die(client.get_error())
    result = series.stats()
    if result:
        result.update({'input': topic,
                       'output': joined_topic,
                       'read': client.get_read()})
    print(result)


def extract_topic(brokers, registry, topic, group, field, num, ignored,
                  filters, debug):
    client = Client(brokers, topic, registry, group, field, debug=debug)
    if not client.open():
        die(client.get_error())
    fargs = filters.split('=')
    series = client.extract(num, ignored, fargs[0], fargs[1])
    if not series:
        die(client.get_error())
    result = series.stats()
    if result:
        result.update({'topic': topic,
                       fargs[0]: fargs[1],
                       'read': client.get_read()})
    print(result)


def avro_file(avrofile, action, namespace, schema, pretty, ppretty, debug):
    af = AvroFile(avrofile)
    if action == 'refactor':
        if not namespace:
            die("namespace must be specified")
        newfile = af.refactor(namespace)
        if not newfile:
            die(af.get_error())
        print("Refactored Avro file:", newfile)
    elif action == 'print':
        af.print_content(Formatter(pretty or ppretty, ppretty), schema)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--debug', action='store_true')
    subparsers = parser.add_subparsers(title='commands')

    sub1 = subparsers.add_parser("list", help="list topics")
    sub1.set_defaults(func=list_topics)
    sub1.add_argument('-b', '--brokers', default=BROKER, required=(not BROKER),
                      help=HELP_BROKERS)
    sub1.add_argument('-r', '--registry', default=REGISTRY, help=HELP_REGISTRY)
    sub1.add_argument('-l', '--long', action='store_true', dest='details',
                      help="show details")

    sub2 = subparsers.add_parser("show", help="show topic schema")
    sub2.set_defaults(func=show_schema)
    sub2.add_argument('-b', '--brokers', default=BROKER, required=(not BROKER),
                      help=HELP_BROKERS)
    sub2.add_argument('-r', '--registry', default=REGISTRY,
                      required=(not REGISTRY), help=HELP_REGISTRY)
    sub2.add_argument('-s', '--sample', action='store_true',
                      help="generate a sample JSON message from schema")
    sub2.add_argument('topic')

    sub3 = subparsers.add_parser("register", help="register a chema")
    sub3.set_defaults(func=register_schema)
    sub3.add_argument('-b', '--brokers', default=BROKER, required=(not BROKER),
                      help=HELP_BROKERS)
    sub3.add_argument('-r', '--registry', default=REGISTRY,
                      required=(not REGISTRY), help=HELP_REGISTRY)
    sub3.add_argument('topic')
    sub3.add_argument('schemafile', type=argparse.FileType('r'))

    sub4 = subparsers.add_parser("print", help="print topic to stdout")
    sub4.set_defaults(func=print_topic)
    sub4.add_argument('-b', '--brokers', default=BROKER, required=(not BROKER),
                      help=HELP_BROKERS)
    sub4.add_argument('-r', '--registry', default=REGISTRY, help=HELP_REGISTRY)
    sub4.add_argument('-g', '--group', help="Kafka consumer Group Id")
    sub4.add_argument('-o', '--output', help='output format', default='json',
                      choices=['json', 'csv', 'bin'])
    sub4.add_argument('-n', '--num', type=int, default=sys.maxsize,
                      help="number of messages to read (default all)")
    sub4.add_argument('-m', '--metadata', action='store_true',
                      help="print Kafka offset, timestamp and key")
    sub4.add_argument('-p', '--pretty', action='store_true',
                      help="pretty print (colors)")
    sub4.add_argument('-P', '--Pretty', action='store_true', dest='ppretty',
                      help="pretty print (colors + indents)")
    sub4.add_argument('-f', '--filters', help="filter expression (k=v)")
    sub4.add_argument('topic')

    sub5 = subparsers.add_parser("join", help="join topics and get measures")
    sub5.set_defaults(func=join_topics)
    sub5.add_argument('-b', '--brokers', default=BROKER, required=(not BROKER),
                      help=HELP_BROKERS)
    sub5.add_argument('-r', '--registry', default=REGISTRY, help=HELP_REGISTRY)
    sub5.add_argument('-g', '--group')
    sub5.add_argument('-n', '--num', type=int, default=sys.maxsize,
                      help="number of messages to read (default all)")
    sub5.add_argument('topic')
    sub5.add_argument('idfield', help="Unique ID field (or json path)")
    sub5.add_argument('joined_topic', help="topic to join with")
    sub5.add_argument('joined_idfield', help="Unique ID field (or json path)")

    sub6 = subparsers.add_parser("count", help="count messages in a topic")
    sub6.set_defaults(func=count_topic)
    sub6.add_argument('-b', '--brokers', default=BROKER, required=(not BROKER),
                      help=HELP_BROKERS)
    sub6.add_argument('topic')

    sub7 = subparsers.add_parser("extract",
                                 help="extract topic data and get measures")
    sub7.set_defaults(func=extract_topic)
    sub7.add_argument('-b', '--brokers', default=BROKER, required=(not BROKER),
                      help=HELP_BROKERS)
    sub7.add_argument('-r', '--registry', default=REGISTRY, help=HELP_REGISTRY)
    sub7.add_argument('-g', '--group')
    sub7.add_argument('-n', '--num', type=int, default=sys.maxsize,
                      help="number of messages to read (default all)")
    sub7.add_argument('-i', '--ignored', type=int, default=0,
                      help="ignore first N records (default 0)")
    sub7.add_argument('-f', '--filters',
                      help="filter expression (k=v)")
    sub7.add_argument('topic')
    sub7.add_argument('field', help="field to extract")

    sub9 = subparsers.add_parser("generate", help="message generator")
    sub9.set_defaults(func=msg_generator)
    sub9.add_argument('-b', '--brokers', default=BROKER, required=(not BROKER),
                      help=HELP_BROKERS)
    sub9.add_argument('-r', '--registry', default=REGISTRY, help=HELP_REGISTRY)
    sub9.add_argument('-d', '--delay', type=int, default=10,
                      help='delay between each message in ms')
    sub9.add_argument('-s', '--seed',  type=int, default=0,
                      help='random seed')
    sub9.add_argument('-n', '--num', type=int, default=sys.maxsize,
                      help="number of messages to generate")
    sub9.add_argument('-o', '--stdout', action='store_true',
                      help="print messages to stdout")
    sub9.add_argument('-c', '--compress', action='store_true',
                      help="enable snappy compression")
    sub9.add_argument('topic', help="output topic")
    sub9.add_argument('message', help='message format in JSON')

    sub10 = subparsers.add_parser("avro", help="Avro file utility")
    sub10.set_defaults(func=avro_file)
    sub10.add_argument('action', choices=['print', 'refactor'])
    sub10.add_argument('avrofile', type=argparse.FileType('rb'))
    sub10.add_argument('-n', '--namespace',
                       help="new namespace (refactor)")
    sub10.add_argument('-s', '--schema', action='store_true',
                       help="print schema")
    sub10.add_argument('-p', '--pretty', action='store_true',
                       help="pretty print (colors)")
    sub10.add_argument('-P', '--Pretty', action='store_true', dest='ppretty',
                       help="pretty print (colors + indents)")

    parser.add_argument('--version', action='version',
                        version="%(prog)s " + __version__)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)
    kwargs = vars(parser.parse_args())
    kwargs.pop('func')(**kwargs)


if __name__ == '__main__':
    main()

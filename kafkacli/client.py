# -*- coding: utf-8 -*-

"""Client class"""

import sys
import re
import uuid
import random
import time
import string
import requests
import io
import json
# package avro-python3!
from avro.io import DatumReader, DatumWriter, BinaryDecoder, BinaryEncoder
from avro.schema import Parse
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer, errors
from kafkacli.timeseries import TimeSeries
from kafkacli.formatter import Formatter

NO_SCHEMA = 'None'
_REGISTRY_HEADERS = {"Content-Type": "application/vnd.schemaregistry.v1+json"}


class Client(object):
    """Main client

    Attributes:
       brokers (str): list of Kafka brokers server:port,...
    """

    def __init__(self, brokers, topic, registry=None, group=None, field=None,
                 latest=False, debug=False):
        self.topic = topic
        self.registry = registry
        self.brokers = brokers
        self.group = group
        self.latest = False
        self.field = field
        self.debug = debug
        # private fields
        self._consumer = None
        self._schemas = {}
        self._readers = {}
        self._writers = {}
        self._lasterror = None
        self._subjects = None
        self._processed = 0
        self._generateNum = None
        self._generateTime = None

    # Accessors
    def get_error(self):
        return self._lasterror

    def get_read(self):
        return self._read

    def open(self):
        if self._consumer:
            return True
        try:
            self._consumer = KafkaConsumer(
                self.topic,
                group_id=self.group,
                bootstrap_servers=self.brokers.split(','),
                auto_offset_reset='latest' if self.latest else 'earliest',
                enable_auto_commit=True if self.group else False,
                consumer_timeout_ms=10000 if self.group else 1000
            )
        except Exception as err:
            self._lasterror = "cannot connect to brokers " + self.brokers
            self._lasterror += " (" + str(err) + ")"
            return False
        if self.registry:
            try:
                req = requests.get(self.registry + "/subjects")
                if req.status_code != requests.codes.ok:
                    self._lasterror = "registry request failure (HTTP code "
                    self._lasterror += str(req.status_code) + ")"
                    return False
                self._subjects = req.text
            except Exception as err:
                self._lasterror = "cannot connect to registry " + self.registry
                self._lasterror += " (" + str(err) + ")"
                return False
        return True

    def close(self):
        if self._consumer:
            self._consumer.close()
        self._consumer = None
        return True

    def get_topics(self, details=False, showall=False):
        topics = sorted(self._consumer.topics())
        if not showall:
            topics = [t for t in topics if t[0:1] != '_']
        if details:
            topics = [[t, 'avro' if (t + "-value") in self._subjects
                       else 'none'] for t in topics]
        return topics

    def get_schema(self):
        return self._get_schema(self.topic)

    def _get_schema(self, topic):
        if topic not in self._schemas:
            if self.registry:
                req = requests.get(self.registry + "/subjects/" + topic +
                                   "-value/versions/latest")
                if req.status_code == requests.codes.not_found:
                    self._schemas[topic] = NO_SCHEMA
                elif req.status_code != requests.codes.ok:
                    client.error = "cannot get schema from registry"
                else:
                    rsp = json.loads(req.text)
                    self._schemas[topic] = rsp['schema']
            else:
                self._schemas[topic] = NO_SCHEMA
        return self._schemas[topic]

    def get_sample_record(self):
        record = {}
        for field in json.loads(self.get_schema())['fields']:
            if 'type' not in field:
                raise Exception("wrong field?", field)
            if 'default' in field:
                record[field['name']] = field['default']
            elif field['type'] == 'long':
                record[field['name']] = random.randint(0, 10000000)
            elif field['type'] == 'double':
                record[field['name']] = random.randint(0, 10000000)/100.0
            elif field['type'] == 'string':
                record[field['name']] = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))  # nopep8
            else:
                raise Exception("unsupported type: " + field['type'])
        return record

    def register_schema(self, schemafile):
        if not self.registry:
            return
        with schemafile as f:
            str = f.read()
        payload = "{ \"schema\": \"" + \
            str.replace("\"", "\\\"").replace(
                "\t", "").replace("\n", "") + "\" }"
        req = requests.post(self.registry + "/subjects/" + self.topic +
                            "-value/versions",
                            headers=_REGISTRY_HEADERS,
                            data=payload)
        if req.status_code != requests.codes.ok:
            client.error = "registration failed"
        return True

    def _decode(self, message, topic):
        schema = self._get_schema(topic)
        if schema == NO_SCHEMA:
            return json.loads(message.value.decode())
        if topic not in self._readers:
            self._readers[topic] = DatumReader(Parse(schema))
        # why 5 ??
        raw = io.BytesIO(message.value[5:])
        decoded = BinaryDecoder(raw)
        return self._readers[topic].read(decoded)

    def _encode(self, value, topic):
        schema = self._get_schema(topic)
        if schema == NO_SCHEMA:
            return json.dumps(value).encode()
        if topic not in self._writers:
            self._writers[topic] = DatumWriter(Parse(schema))
        bytes_writer = io.BytesIO()
        encoder = BinaryEncoder(bytes_writer)
        self._writers[topic].write(value, encoder)
        return bytes_writer.getvalue()

    def print_topic(self, formatter, output='json', num=sys.maxsize,
                    metadata=False, ffield=None, fvalue=None):
        n = 0
        record = None
        for msg in self._consumer:
            if output == 'bin':
                print(msg.value)
                n += 1
            else:
                record = {}
                if metadata:
                    record.update({"_partition": msg.partition,
                                   "_offset": msg.offset,
                                   "_timestamp": msg.timestamp})
                if msg.key:
                    record["_key"] = msg.key
                record.update(self._decode(msg, self.topic))
                if (not ffield) or (ffield in record and
                                    str(record[ffield]) == fvalue):
                    if output == 'json':
                        formatter.print(record)
                    elif output == 'csv':
                        print(",".join([str(v) for k, v in record.items()]))
                    else:
                        print(record)
                    n += 1
            if n >= num:
                break
        self._read = n
        return record

    def read_topic(self, action=None):
        n = 0
        for msg in self._consumer:
            if action:
                print("TODO")
            n += 1
        self._read = n

    def join(self, joined_topic, joined_field, num):
        series = TimeSeries()
        # first read main topics and store uuid/timestamp in this dict
        ts = {}
        n = 0
        keys = self.field.split(".")
        for msg in self._consumer:
            record = self._decode(msg, self.topic)
            recid = record
            for k in keys:
                if k not in recid:
                    self._lasterror = "key " + self.field + " not found in "
                    self._lasterror += str(record)
                    return None
                recid = recid[k]
            if not isinstance(recid, str):
                self._lasterror = str(recid) + " is not a key (check args)"
                return None
            ts[recid] = msg.timestamp
            n += 1
            if n >= num:
                break
            if self.debug and n % 1000 == 0:
                print("# ", n, "records read from topic", self.topic)
        n = 0
        # then open a second consumer for the joined topics
        consumer = KafkaConsumer(
            joined_topic,
            group_id=self.group,
            bootstrap_servers=self.brokers.split(','),
            auto_offset_reset='earliest',
            enable_auto_commit=True if self.group else False,
            consumer_timeout_ms=20000 if self.group else 2000
        )
        keys = joined_field.split(".")
        for msg in consumer:
            record = self._decode(msg, joined_topic)
            recid = record
            for k in keys:
                if k not in recid:
                    self._lasterror = "key " + joined_field + " not found in "
                    self._lasterror += str(record)
                    return None
                recid = recid[k]
            if not isinstance(recid, str):
                self._lasterror = str(recid) + " is not a key (check args)"
                return None
            # do the join
            if recid in ts:
                # in theory the timestamp is always greater
                if (msg.timestamp > ts[recid]):
                    series.append(ts[recid], msg.timestamp - ts[recid])
                # remove the entry
                del[recid]
            n += 1
            if n >= num:
                break
            if self.debug and n % 1000 == 0:
                print("# ", n, "records joined with topic", joined_topic)
        self._read = n
        return series

    def extract(self, num=sys.maxsize, ignore=0, ffield=None, fvalue=None):
        series = TimeSeries()
        n = 0
        for msg in self._consumer:
            record = self._decode(msg, self.topic)
            if not ffield or (ffield in record and record[ffield] == fvalue):
                if n >= ignore:
                    series.append(msg.timestamp, record[self.field])
                n += 1
                if n >= num:
                    break
                if self.debug and n % 1000 == 0:
                    print("# ", n, "records read from topic", self.topic)
        self._read = n
        return series

    def _getTime(self, increment=0, date=False):
        if self._generateNum and increment > 0:
            if not self._generateTime:
                self._generateTime = int(time.time()) - \
                                     increment * self._generateNum
            else:
                self._generateTime += increment
            dt = datetime.fromtimestamp(self._generateTime)
        else:
            dt = datetime.now()
        ts = dt.replace(microsecond=0).isoformat()
        if date:
            return ts[0:10]
        return ts

    def generate(self, template, delay, seed, num, stdout=False,
                 compress=False):
        if seed > 0:
            random.seed(seed)
        if self.debug:
            num = 10
            print("# Debug mode, generating", num, "sample messages --")
        tags = re.findall("%[A-Z]+[0-9]*", template)
        funcs = []
        self._generateTime = None
        if num != sys.maxsize:
            self._generateNum = num
        else:
            self._generateNum = None
        # double the brackets to support format function
        template = template.replace("{", "{{").replace("}", "}}")
        for tag in tags:
            template = template.replace(tag, "{}", 1)
            if (tag == "%UUID"):
                funcs.append(lambda:
                             str(uuid.UUID(int=random.getrandbits(128))))
            # pseudo ID using the seed
            elif (tag[0:3] == "%ID"):
                n = int(tag[3:])
                funcs.append(lambda n=n: ''.join(random.choice(
                    string.ascii_lowercase) for _ in range(n)))
            elif (tag[0:4] == "%INT"):
                n = int(tag[4:]) + 1
                funcs.append(lambda n=n: random.randint(0, n))
            elif (tag[0:4] == "%STR"):
                n = int(tag[4:])
                funcs.append(lambda n=n:
                             "".join(random.choices(string.ascii_uppercase,
                                                    k=n)))
            elif (tag[0:5] == "%DATE"):
                n = int(tag[5:]) * 86400
                funcs.append(lambda n=n, s=self: s._getTime(n, date=True))
            elif (tag[0:5] == "%TIME"):
                n = int(tag[5:])
                funcs.append(lambda n=n, s=self: s._getTime(n))
            else:
                raise Exception("unknown tag", tag)
        producer = KafkaProducer(
            bootstrap_servers=self.brokers.split(','),
            compression_type='snappy' if compress else None)
        cnt = 0
        msg = None
        while cnt < num:
            args = [f() for f in funcs]
            msg = json.loads(template.format(*args))
            if self.debug or stdout:
                print(str(msg).replace("'", "\""))
            else:
                producer.send(self.topic, self._encode(msg, self.topic))
                if delay > 0:
                    time.sleep(delay/1000.0)
            cnt += 1
            if not self.debug and not stdout and delay > 0 and cnt % 1000 == 0:
                now = datetime.now().strftime("%H:%M:%S")
                print(now, cnt, "message posted on topic:", self.topic,
                      "(type CTRL^C to stop the process)")
        producer.flush()
        return msg

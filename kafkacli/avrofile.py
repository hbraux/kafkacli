# -*- coding: utf-8 -*-

"""AvroFile Class"""

import io
import json
import sys
from avro.io import DatumReader, DatumWriter
from avro.datafile import DataFileReader, DataFileWriter
from avro.schema import Parse
from kafkacli.formatter import Formatter


class AvroFile(object):
    """AvroFile

    Attributes:
       reader: Buffered Reader to Avro file
    """

    def __init__(self, reader, debug=False):
        self.reader = reader
        self._lasterror = None

    def get_error(self):
        return self._lasterror

    def print_content(self, formatter, schemaonly=False):
        dfr = DataFileReader(io.BytesIO(self.reader.read()), DatumReader())
        records = []
        if schemaonly:
            formatter.print(json.loads(dfr.meta['avro.schema']
                                       .decode("utf-8")))
        else:
            for record in dfr:
                formatter.print(record)

    def refactor(self, namespace):
        dfr = DataFileReader(io.BytesIO(self.reader.read()), DatumReader())
        if 'avro.schema' not in dfr.meta:
            self._lasterror = "cannot read schema from File"
            return None
        js = json.loads(dfr.meta['avro.schema'].decode("utf-8"))
        if namespace:
            old = js['namespace']
            js['namespace'] = namespace
            js['connect.name'] = js['connect.name'].replace(old, namespace)
        schema = Parse(json.dumps(js))
        newfile = self.reader.name.replace(".avro", "_refactored.avro")
        dfw = DataFileWriter(open(newfile, "wb"), DatumWriter(), schema)
        for r in dfr:
            dfw.append(r)
        dfw.close()
        return newfile

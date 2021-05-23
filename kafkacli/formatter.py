# -*- coding: utf-8 -*-

"""Format Class"""

import io
import json
import sys

from pygments import highlight, lexers, formatters, token, style


class Formatter(object):
    """A JSON Pretty Formater

    Attributes:
       colors: with colors
       indents: with indentations
    """

    def __init__(self, colors=False, indents=False):
        self._indent = 4 if indents else None
        self._ft = None
        if colors:
            class _Style(style.Style):
                styles = {
                    token.Token.String: 'ansiblue',
                    token.Token.Number: 'ansired',
                }
            self._ft = formatters.Terminal256Formatter(style=_Style)

    def print(self, data):
        if self._ft:
            sys.stdout.write(highlight(json.dumps(data, indent=self._indent),
                                       lexers.JsonLexer(), self._ft))
        else:
            print(json.dumps(data, indent=self._indent))

#!/usr/bin/env python
"""Dump schema of vector tiles required by Mapbox GL style JSON.
Usage:
  gl-style-schema.py dump <json_spec>
  gl-style-schema.py (-h | --help)
  gl-style-schema.py --version
Options:
  -h --help                 Show this screen.
  --version                 Show version.
"""
import yaml
import collections
from docopt import docopt


def extract_filter_fields(expr):
    if len(expr) < 1:
        return

    def is_combining_filter(f):
        return f in ['all', 'any', 'none']

    def is_existential_filter(f):
        return f in ['has', '!has']

    def is_comparison_filter(f):
        return f in ["==", "!=", ">", ">=", "<", "<="]

    def is_membership_filter(f):
        return f in ['in', '!in']

    fname = expr[0]

    if (is_existential_filter(fname) or is_comparison_filter(fname) or
       is_membership_filter(fname)):
            if expr[1][0] != '$':
                yield expr[1]

    elif is_combining_filter(fname):
        for subexpr in expr[1:]:
            if subexpr[1][0] != '$':
                yield subexpr[1]


def extract_text_field(layer):
    try:
        text_field = layer['layout']['text-field']
        if '{' == text_field[0] and '}' == text_field[-1]:
            yield text_field[1:-1]
    except KeyError:
        pass


def find_layers(spec):
    for layer in spec['layers']:

        if 'source-layer' in layer:
            source = layer['source-layer']

            filter_fields = list(extract_filter_fields(layer.get('filter', [])))
            text_fields = list(extract_text_field(layer))

            yield (source, filter_fields + text_fields)


if __name__ == '__main__':
    args = docopt(__doc__, version=1)
    spec_file = args['<json_spec>']
    spec = yaml.load(open(spec_file))

    layers = collections.defaultdict(dict)
    for source, fields in find_layers(spec):
        for field in fields:
            try:
                layers[source][field] = True
            except TypeError:
                pass

    for layer, fields in layers:
        print(layer)
        print(['-'] * 10)
        for field_name in fields.keys():
            print(field_name)

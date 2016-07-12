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
import re
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
            yield expr[1]

    elif is_combining_filter(fname):
        for subexpr in expr[1:]:
            yield subexpr[1]


def find_tokens(obj):
    "Find {tokens} referencing a data property to pull from"

    def extract_tokens(val):
        match = re.search('{(\w*)}', val)
        if match:
            return match.groups()
        else:
            return []

    for key, val in obj.items():
        if isinstance(val, str):
            for token in extract_tokens(val):
                yield token


def is_special_key(key):
    return key[0] == '$'


def extract_layout_fields(layer):
    if 'layout' not in layer:
        return

    for field in find_tokens(layer['layout']):
        yield field


def find_layers(spec):
    for layer in spec['layers']:

        if 'source-layer' in layer:
            source = layer['source-layer']

            filter_fields = list(extract_filter_fields(layer.get('filter', [])))
            layout_fields = list(extract_layout_fields(layer))

            fields = filter_fields + layout_fields
            yield Layer(
                source,
                [k for k in fields if not is_special_key(k)]
            )


class Layer(object):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


if __name__ == '__main__':
    args = docopt(__doc__, version=1)
    spec_file = args['<json_spec>']
    spec = yaml.load(open(spec_file))

    layers = collections.defaultdict(dict)
    for layer in find_layers(spec):
        for field in layer.fields:
            try:
                layers[layer.name][field] = True
            except TypeError:
                pass

    for source, fields in layers.items():
        print('[{0}]'.format(source))
        for field_name in fields.keys():
            print(field_name)
        print('-' * 10)

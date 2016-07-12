#!/usr/bin/env python
import json
import re
import sys
import argparse


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


def parse_style_layers(spec):
    schema = VectorSchema()
    for layer in spec['layers']:
        if 'source-layer' in layer:
            source = layer['source-layer']
            for field in extract_filter_fields(layer.get('filter', [])):
                schema.add_field(source, field)
    return schema


def parse_tilejson_layers(spec):
    schema = VectorSchema()
    for layer in spec['vector_layers']:
        source = layer['id']
        for field in layer['fields'].keys():
            schema.add_field(source, field)
    return schema


class VectorSchema(object):
    def __init__(self):
        self.layers = {}

    def add_field(self, layer_name, field_name):
        if layer_name not in self.layers:
            self.layers[layer_name] = Layer(layer_name)

        if not is_special_key(field_name):
            self.layers[layer_name].add_field(field_name)

    def __str__(self):
        layers = sorted(self.layers.values(), key=lambda l: l.name)
        return '\n'.join([l.__str__() for l in layers])


class Layer(object):
    def __init__(self, name):
        self.name = name
        self.fields = set()

    def add_field(self, field_name):
        try:
            self.fields.add(field_name)
        # Ignore fields that are strings (false positives)
        except TypeError:
            pass

    def __str__(self):
        lines = ['#{0}'.format(self.name)]
        for field_name in sorted(self.fields):
            lines.append('  [{0}]'.format(field_name))
        return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('specfile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    args = parser.parse_args()
    spec = json.loads(args.specfile.read())

    if 'tilejson' in spec and 'vector_layers' in spec:
        schema = parse_tilejson_layers(spec)
    elif 'layers' in spec:
        schema = parse_style_layers(spec)
    else:
        sys.exit('Input is neither a valid TileJSON spec or Mapbox GL style')

    print(schema)

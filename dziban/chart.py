import json
from copy import deepcopy
import re

from draco.js import data2schema, schema2asp
from draco.run import run as draco
from vega import VegaLite

from dziban.encoding import Encoding

class Chart:
  DEFAULT_NAME = '\"view\"'

  def __init__(self, data):
    self._data = data

    json_data = json.loads(data.to_json(orient='records'))
    self._schema = data2schema(json_data)
    self._encodings = { field : Encoding(field) for field in self._schema['stats'].keys()}

    self.fields = list(self._encodings.keys())

    self._name = 'v'

    self._anchors = {}

    self._mark = None

  def mark(self, value):
    self._mark = value
    return self

  def __getitem__(self, key):
    return self._encodings[key]

  def as_asp(self, viewname, fields):
    vid = viewname
    asp = ['visualization({0}).'.format(vid)]
    asp += schema2asp(self._schema)

    if (self._mark is not None):
      mark = 'mark({0},{1}).'.format(vid, self._mark)
      asp.append(mark)

    for i, field in enumerate(fields):
      eid = 'e{0}'.format(i)
      asp += self._encodings[field].to_asp(vid, eid)

    return asp

  def see(self, *fields, anchor=None, name=None):
    if (name is not None):
      viewname = '\"{0}\"'.format(name)
    else:
      viewname = Chart.DEFAULT_NAME

    partial = self.as_asp(viewname, fields)
    asp = [] + partial

    if (anchor is not None):
      anchor = '\"{0}\"'.format(anchor)
      asp += self._anchors[anchor]

    self._sol = draco(asp)

    if (name is not None):
      self._anchors[viewname] = anchor_spec(partial, self._sol.props)


    return VegaLite(self._sol.as_vl(viewname), self._data)

def anchor_spec(partial, complete):
  REGEX = re.compile(r'(\w+)\(([\w\.\"\/]+)(,([\w\"\.]+))?(,([\w\.\"]+))?\)')

  asp = partial + complete

  def inc_predicate(dict, pred):
    (count, params) = dict[pred]
    dict[pred] = (count + 1, params)

  predicates = {}
  for fact in complete:
    [predicate, v, _, __, ___, ____] = REGEX.findall(fact)[0]
    if (predicate == 'visualization'):
      vis = v

    if (predicate in ('visualization', 'mark')):
      continue
    elif (predicate in ('encoding', 'zero', 'log')):
      if (predicate not in predicates): predicates[predicate] = (0, 1)
      inc_predicate(predicates, predicate)
    elif (predicate in ('field', 'type', 'channel', 'bin')):
      if (predicate not in predicates): predicates[predicate] = (0, 2)
      inc_predicate(predicates, predicate)

  for p in predicates:
    (count, params) = predicates[p]
    constraint = ':- not {{ {0}({1}'.format(p,vis)
    for _ in range(params):
      constraint += ',_'
    constraint += ') }} = {0}.'.format(count)
    asp.append(constraint)

  return asp

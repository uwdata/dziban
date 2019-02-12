from typing import List
from draco.run import run as run_draco
from draco.js import cql2asp
from draco.helper import data_to_asp
import json
import re

from dziban.mark import VizMark
from dziban.encoding import VizEncoding

class Viz(VizMark, VizEncoding):
  def __init__(self, data=None):
    VizMark.__init__(self)
    VizEncoding.__init__(self)

    self._data = data
    self._strict = False
    return

  def strict(self):
    self._strict = True
    return self


  def _spec(self):
    spec = {}
    
    partial = self._is_partial()
    
    if (partial and self._strict):
      raise Error('cannot be both partial and strict')

    return {
      **self.build_encoding(),
      **self.build_mark()
    }

  def _schema(self):
    json_data = json.loads(self._data.to_json(orient='records'))
    return data_to_asp(json_data)

  def build(self):
    if (self._strict):
      return self._spec()
    else:
      spec = self._spec()
      schema = self._schema()
      asp = cql2asp(spec) + schema

      result = run_draco(asp)
      return EditViz(self,result)

  def _is_partial(self):
    return (
      not self._strict or
      self._encoding_partial() and
      self._mark_partial()
    )

REGEX = re.compile(r'(\w+)\(([\w\.\"\/]+)(,([\w\"\.]+))?(,([\w\.\"]+))?\)')

class EditViz(Viz):
  def __init__(self, original, result):
    self.__dict__ = original.__dict__.copy()
    self.result = result
  
  def build(self):
    vis = None
    asp = []
    asp += self.result.props

    predicates = {}
    for fact in self.result.props:
      [predicate, v, _, first, __, second] = REGEX.findall(fact)[0]
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
      for i in range(params):
        constraint += ',_'
      constraint += ') }} = {0}.'.format(count)
      asp.append(constraint)

    print('\n'.join(asp))

    v2 = cql2asp(self._spec())
    for i, rule in enumerate(v2):
      if ('v1' in rule):
        v2[i] = rule.replace('v1', 'v2')
    
    asp += v2

    asp += self._schema()

    result = run_draco(asp)
    return result

def inc_predicate(dict, pred):
  (count, params) = dict[pred]
  dict[pred] = (count + 1, params)

  
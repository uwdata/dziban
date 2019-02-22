from copy import deepcopy
import re

from draco.js import data2schema, schema2asp
from draco.run import run as draco
from vega import VegaLite

from .field import Field
from .base import Base

class Chart(Field):
  DEFAULT_NAME = '\"view\"'
  ANCHOR_NAME = '\"anchor\"'

  def __init__(self, data):
    Base.__init__(self, data)
    self._mark = None
    self._name = Chart.DEFAULT_NAME

  def mark(self, value):
    clone = self.clone()
    clone._mark = value
    return clone

  def _get_asp_partial(self):
    vid = self._name
    asp = ['visualization({0}).'.format(vid)]
    asp += schema2asp(self._schema)

    if (self._mark is not None):
      mark = 'mark({0},{1}).'.format(vid, self._mark)
      asp.append(mark)

    for i, field in enumerate(self._selectedfields):
      eid = 'e{0}'.format(i)
      asp += self._encodings[field].to_asp(vid, eid)

    return asp

  def _get_draco_sol(self):
    partial = self._get_asp_partial()
    anchor = self._get_anchor_asp()

    query = partial + anchor
    sol = draco(query)
    return sol

  def _get_asp_complete(self):
    sol = self._get_draco_sol()
    return sol.props[self._name]

  def anchor(self, other):
    clone = self.clone()

    anchor_clone = other.clone()
    anchor_clone._name = Chart.ANCHOR_NAME

    clone._anchor = anchor_clone
    return clone

  def _get_anchor_asp(self):
    if (self._anchor is None):
      return []
    
    REGEX = re.compile(r'(\w+)\(([\w\.\"\/]+)(,([\w\"\.]+))?(,([\w\.\"]+))?\)')

    anchor_complete = self._anchor._get_asp_complete()
    asp = ['base({0}).'.format(self._anchor._name)] + anchor_complete

    def inc_predicate(dict, pred):
      (count, params) = dict[pred]
      dict[pred] = (count + 1, params)

    predicates = {}
    for fact in anchor_complete:
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

  def _get_render(self):
    sol = self._get_draco_sol()

    vegalite = sol.as_vl(Chart.DEFAULT_NAME)
    return VegaLite(vegalite, self._data)

  def _repr_mimebundle_(self, include=None, exclude=None):
    return self._get_render()._repr_mimebundle_(include, exclude)

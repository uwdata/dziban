from copy import deepcopy
import re
import json

from draco.js import data2schema, schema2asp
from draco.run import run as draco, DRACO_LP
from vega import VegaLite
from scipy.stats import zscore

from .base import Base
from .field import Field
from .channel import Channel
from .util import filter_sols, foreach, construct_graph, normalize

class Chart(Field, Channel):
  DEFAULT_NAME = '\"view\"'
  ANCHOR_NAME = '\"anchor\"'
  OPT_GRAPHSCAPE_FILES = list(filter(lambda file : file != 'optimize.lp', DRACO_LP)) + ['optimize_graphscape.lp']
  OPT_DRACO_FILES = list(filter(lambda file : file != 'optimize.lp', DRACO_LP)) + ['optimize_draco.lp']
  K = 20

  def __init__(self, data):
    Base.__init__(self, data)
    Field.__init__(self)
    Channel.__init__(self)
    self._id = 0
    self._mark = None
    self._name = Chart.DEFAULT_NAME

  def mark(self, value):
    clone = self.clone()
    clone._mark = value
    return clone

  def get_fields(self):
    return self._fields

  def is_satisfiable(self):
    return self._get_draco_sol() is not None

  def __sub__(self, other):
    query = self.anchor_on(other)._get_anchor_asp() + self._get_asp_complete()
    
    files = ['compare.lp']
    result = draco(query, files=files, silence_warnings=True)
    return result.graphscape_list

  def __getitem__(self, key):
    topk = self._get_topk_from_anchor()
    return self._set_sol(topk[key][0])

  def _get_asp_partial(self):
    vid = self._name
    asp = ['visualization({0}).'.format(vid)]
    asp += schema2asp(self._schema)

    if (self._mark is not None):
      mark = 'mark({0},{1}).'.format(vid, self._mark)
      asp.append(mark)

    min_encodings = max([len(x) for x in [self._selectedfields, self._selectedchannels]])

    for i in range(min_encodings):
      eid = 'e{0}'.format(i)
      asp.append('encoding({0},{1}).'.format(vid, eid))

    for enc in self._encodings:
      asp += enc.to_asp(vid)

    return asp

  def _get_draco_sol(self):
    if (self._solved):
      return self._sol

    sol = None
    if (self._anchor):
      topk = self._get_topk_from_anchor()
      sol = topk[0][0]
    else:
      query = self._get_full_query()
      sol = draco(query)
    
    self._solved = True
    self._sol = sol

    return sol

  def _get_full_query(self):
    partial = self._get_asp_partial()
    anchor = self._get_anchor_asp()

    query = partial + anchor

    return query

  def _get_draco_rank(self):
    return self._get_rank('draco')

  def _get_graphscape_rank(self, anchor_for_cold=None):
    return self._get_rank('graphscape', anchor_for_cold)

  def _get_rank(self, function, anchor_for_cold=None):
    opt = None

    if (function == 'graphscape'):
      opt = Chart.OPT_GRAPHSCAPE_FILES
    elif (function == 'draco'):
      opt = Chart.OPT_DRACO_FILES
    else:
      raise Exception("invalid function (graphscape or draco)")

    best_vegalite = json.dumps(self._get_vegalite(), sort_keys=True)
      

    query = None

    if (function == 'graphscape'):
      if (anchor_for_cold):
        query = self.clone().anchor_on(anchor_for_cold)._get_full_query()
      else:
        if self._anchor is None:
          raise Exception("cold recommendation requires an anchor_for_cold")
        query = self._get_full_query()
    elif (function == 'draco'):
      query = self._get_asp_partial()

    topk = draco(query, files=opt, topk=True, k=Chart.K, silence_warnings=True)

    topk_vegalite = { json.dumps(c.as_vl(Chart.DEFAULT_NAME), sort_keys=True):rank for rank, c in enumerate(topk) }

    if (best_vegalite in topk_vegalite):
      return topk_vegalite[best_vegalite]
    else:
      return None

  def _get_topk_from_anchor(self):
    query = self._get_full_query()
    best = draco(query, files=Chart.OPT_GRAPHSCAPE_FILES, topk=True, k=Chart.K, silence_warnings=True)

    good = filter_sols(best)
    
    if (len(good) == 1):
      return [(good[0],0)]

    d = [v.d for v in good]
    g = [v.g for v in good]

    # print(d)
    # print(g)
    dz = None
    gz = None
    if (len(set(d)) == 1):
      dz = [0 for _ in d]
    else:
      # dz = zscore(d)
      dz = normalize(d)

    if (len(set(g)) == 1):
      gz = [0 for _ in g]
    else:
      # gz = zscore(g)
      gz = normalize(g)

    # print(dz)
    # print(gz)

    combined = [(v, dz[i] + gz[i], d[i]) for i,v in enumerate(good)]
    combined.sort(key = lambda x : (x[1], x[2]))

    return combined

  def _get_asp_complete(self):
    sol = self._get_draco_sol()
    return sol.props[self._name]

  def _get_violations(self):
    sol = self._get_draco_sol()
    return sol.violations

  def _get_graphscape_list(self):
    sol = self._get_draco_sol()
    return sol.graphscape_list

  def _get_facts(self):
    sol = self._get_draco_sol()
    return sol.draco_list

  def anchor_on(self, other):
    clone = self.clone()

    anchor_clone = other.clone()
    anchor_clone._name = Chart.ANCHOR_NAME[:-1] + str(clone._id) + '\"'
    clone._id += 1

    clone._anchor = anchor_clone
    return clone

  def _get_anchor_asp(self):
    if (self._anchor is None):
      return []
    
    REGEX = re.compile(r'(\w+)\(([\w\.\"\/]+)(,([\w\"\.]+))?(,([\w\.\"]+))?\)')

    anchor_complete = self._anchor._get_asp_complete()
    asp = ['base({0}).'.format(self._anchor._name)] + anchor_complete

    return asp

  def _get_vegalite(self):
    return self._get_draco_sol().as_vl(Chart.DEFAULT_NAME)

  def _get_render(self):
    return VegaLite(self._get_vegalite(), self._data)

  def _repr_mimebundle_(self, include=None, exclude=None):
    return self._get_render()._repr_mimebundle_(include, exclude)
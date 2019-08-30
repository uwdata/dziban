from copy import deepcopy

class Encoding(object):
  CHANNELS = ['x', 'y', 'row', 'column', 'color', 'size', 'shape', 'text']
  
  def __init__(self, **condition):
    if (len(condition.keys()) != 1):
      raise ValueError('only one condition allowed')

    self._condition = next(iter(condition.items()))
    if (self._condition[0] == 'field'):
      self._condition = (self._condition[0], '\"{0}\"'.format(self._condition[1]))

    self._field = None
    self._ftype = None
    self._aggregate = None
    self._channel = None
    self._bin = None
    self._maxbins = None
    self._scale = None

  def clone(self):
    return deepcopy(self)

  def ftype(self, value):
    self._ftype = value
    return self

  def field(self, value):
    self._field = value
    return self

  def aggregate(self, value):
    self._aggregate = value
    return self

  def channel(self, value):
    self._channel = value
    return self

  def bin(self, value):
    self._bin = value
    return self

  def maxbins(self, value):
    self._bin = True
    self._maxbins = value
    return self

  def scale(self, value):
    self._scale = value
    return self

  def to_asp(self, vid):
    asp = []
    facts = []
    eid = 'E'

    condition_key = self._condition[0]
    condition_value = self._condition[1]
    condition = '{0}({1},{2},{3})'.format(condition_key, vid, eid, condition_value)

    declare = ':- not {0} : encoding({1},E).'.format(condition, vid)
    asp.append(declare)

    template = '{0}({1},{2},{3})'

    if (self._field is not None):
      field = template.format('field', vid, eid, '\"{0}\"'.format(self._field))
      facts.append(field)

    if (self._ftype is not None):
      ftype = template.format('type', vid, eid, self._ftype)
      facts.append(ftype)

    if (self._aggregate is not None):
        aggregate = template.format('aggregate', vid, eid, self._aggregate)
        facts.append(aggregate)

    if (self._channel is not None):
      channel = template.format('channel', vid, eid, self._channel)
      facts.append(channel)

    if (self._bin is not None):
      bins = 10 if self._maxbins is None else self._maxbins
      bin = template.format('bin', vid, eid, bins)
      facts.append(bin)

    if (self._scale is not None):
      if (self._scale == 'log'):
        scale = 'log({0},{1})'.format(vid, eid)
        facts.append(scale)

    conditioned_facts = [':- not {0} : {1}.'.format(f, condition) for f in facts]

    asp += conditioned_facts
    return asp
    
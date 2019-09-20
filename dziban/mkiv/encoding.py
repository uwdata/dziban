from copy import deepcopy
import json

class Encoding(object):
  CHANNELS = ['x', 'y', 'row', 'column', 'color', 'size', 'shape', 'text']
  
  def __init__(self, **condition):
    if (len(condition.keys()) != 1):
      raise ValueError('only one condition allowed')

    self._condition = next(iter(condition.items()))
    if (self._condition[0] == 'field'):
      self._condition = (self._condition[0], '\"{0}\"'.format(self._condition[1]))

    self._field = False
    self._type = False
    self._aggregate = False
    self._channel = False
    self._bin = None
    self._maxbins = False
    self._scale = False

  def clone(self):
    return deepcopy(self)

  def type(self, value):
    self._type = value
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

    declare = None
    condition = None
    if (condition_key == 'aggregate' and condition_value == None):
      declare = ':- aggregate({0},_,count).'.format(vid)
    else:
      condition = '{0}({1},{2},{3})'.format(condition_key, vid, eid, condition_value)
      declare = ':- not {0} : encoding({1},E).'.format(condition, vid)

    asp.append(declare)

    template = '{0}({1},{2},{3})'
    none_template = 'not {0}({1},{2},_)'

    if (self._field is not False):
      field = None

      if (self._field is None):
        field = none_template.format('field', vid, eid)
      else:
        field = template.format('field', vid, eid, '\"{0}\"'.format(self._field))
      facts.append(field)

    if (self._type is not False):
      type = None

      if (self._type is None):
        type = none_template.format('type', vid, eid)
      else:
        type = template.format('type', vid, eid, self._type)

      facts.append(type)

    if (self._aggregate is not False):
      aggregate = None
      if (self._aggregate is None):
        aggregate = none_template.format('aggregate', vid, eid)
      else:
        aggregate = template.format('aggregate', vid, eid, self._aggregate)
      facts.append(aggregate)

    if (self._channel is not False):
      channel = None
      
      if (self._channel is None):
        channel = none_template.format('channel', vid, eid)
      else:
        channel = template.format('channel', vid, eid, self._channel)
      facts.append(channel)

    if (self._bin is not None):
      bin = None
      if (self._bin is False):
        bin = none_template.format('bin', vid, eid)
      else:
        bins = 10 if self._maxbins is False else self._maxbins
        bin = template.format('bin', vid, eid, bins)
      facts.append(bin)

    if (self._scale is not False):
      if (self._scale == 'log'):
        scale = 'log({0},{1})'.format(vid, eid)
      elif (self._scale == 'zero'):
        scale = 'zero({0},{1})'.format(vid, eid)
      facts.append(scale)

    conditioned_facts = [':- {0}, not {1}.'.format(condition, f) for f in facts]

    asp += conditioned_facts
    return asp
    
  def __repr__(self):
    return json.dumps(self.__dict__)

  def __str__(self):
    return json.dumps(self.__dict__)
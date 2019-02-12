class Encoding(object):
  def __init__(self, field):
    self._field = field

    self._aggregate = None
    self._channel = None
    self._bin = None
    self._maxbins = None
    self._scale = None

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

  def to_asp(self, vid, eid):
    rules = []

    decl = 'encoding({0},{1}).'.format(vid, eid)
    rules.append(decl)

    field = ':- not field({0},{1},\"{2}\").'.format(vid, eid, self._field)
    rules.append(field)

    template = '{0}({1},{2},{3}).'

    if (self._aggregate is not None):
      aggregate = template.format('aggregate', vid, eid, self._aggregate)
      rules.append(aggregate)

    if (self._channel is not None):
      channel = template.format('channel', vid, eid, self._channel)
      rules.append(channel)

    if (self._bin is not None):
      bins = 10 if self._maxbins is None else self._maxbins
      bin = template.format('bin', vid, eid, bins)
      rules.append(bin)

    if (self._scale is not None):
      if (self._scale == 'log'):
        scale = 'log({0},{1}).'.format(vid, eid)
        rules.append(scale)

    return rules
    
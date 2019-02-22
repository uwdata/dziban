from .base import Base
from .util import foreach

class Field(Base):
  def field(
    self,
    *fields,
    channel = None,
    aggregate = None,
    scale = None,
    bin = None,
    maxbins = None
  ):
    clone = self.clone()
    clone._selectedfields.update(fields)
    ev = [clone._encodings[f] for f in fields]

    if (channel is not None):
      foreach(ev, lambda x : x.channel(channel))

    if (aggregate is not None):
      foreach(ev, lambda x : x.aggregate(aggregate))

    if (scale is not None):
      foreach(ev, lambda x : x.scale(scale))

    if (bin is not None):
      foreach(ev, lambda x : x.bin(bin))

    if (maxbins is not None):
      foreach(ev, lambda x : x.maxbins(maxbins))

    return clone
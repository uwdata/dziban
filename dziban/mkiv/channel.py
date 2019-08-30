from .base import Base
from .encoding import Encoding
from .util import foreach

class Channel(Base):
  def __init__(self):
    self._selectedchannels = set()

    for c in Encoding.CHANNELS:
      def f(self, c=c, **props):
        clone = self.clone()

        enc = Encoding(channel=c)

        clone._selectedchannels.add(c)

        for k, v in props.items():
          getattr(enc, k)(v)

        clone._encodings.append(enc)
        return clone
        
      setattr(self.__class__, c, f)

  def channel(
    self,
    *channels,
    **props,
  ):
    clone = self.clone()
    self._selectedchannels.update(channels)

    clone._update_encodings('channel', channels, props)
    
    return clone


        
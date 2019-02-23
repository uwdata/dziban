from .base import Base
from .encoding import Encoding
from .util import foreach

class Channel(Base):
  def __init__(self):
    for c in Encoding.CHANNELS:
      def f(**props):
        that = self
        clone = that.clone()
        ev = filter(lambda e : e._channel == c, clone._encodings.values())

        for k, v in props.items():
          foreach(ev, lambda x : getattr(x, k)(v))
        
        return clone
        
      setattr(self, c, f)


        
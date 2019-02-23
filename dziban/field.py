from .base import Base
from .util import foreach

class Field(Base):
  def field(
    self,
    *fields,
    **props,
  ):
    clone = self.clone()
    clone._selectedfields.update(fields)
    ev = [clone._encodings[f] for f in fields]

    for k, v in props.items():
      foreach(ev, lambda x : getattr(x, k)(v))
    
    return clone
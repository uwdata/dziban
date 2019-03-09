from .base import Base
from .util import foreach
from .encoding import Encoding

class Field(Base):
  def __init__(self):
    self._selectedfields = set()

  def field(
    self,
    *fields,
    **props,
  ):
    clone = self.clone()
    clone._selectedfields.update(fields)

    clone._update_encodings('field', fields, props)
    
    return clone
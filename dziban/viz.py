from typing import List

from dziban.mark import VizMark
from dziban.encoding import VizEncoding

class Viz(VizMark, VizEncoding):
  def __init__(self):
    VizMark.__init__(self)
    VizEncoding.__init__(self)
    
    self._strict = False
    return

  def strict(self):
    self._strict = True
    return self

  def build(self):
    spec = {}
    
    partial = self._is_partial()
    
    if (partial and self._strict):
      raise Error('cannot be both partial and strict')

    return {
      **self.build_encoding(),
      **self.build_mark()
    }

  def _is_partial(self):
    return (
      not self._strict or
      self._encoding_partial() and
      self._mark_partial()
    )
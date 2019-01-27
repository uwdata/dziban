from typing import List
from draco.run import run as run_draco
from draco.js import cql2asp
from draco.helper import data_to_asp
import json

from dziban.mark import VizMark
from dziban.encoding import VizEncoding

class Viz(VizMark, VizEncoding):
  def __init__(self, data=None):
    VizMark.__init__(self)
    VizEncoding.__init__(self)

    self._data = data
    self._strict = False
    return

  def strict(self):
    self._strict = True
    return self


  def _spec(self):
    spec = {}
    
    partial = self._is_partial()
    
    if (partial and self._strict):
      raise Error('cannot be both partial and strict')

    return {
      **self.build_encoding(),
      **self.build_mark()
    }

  def _schema(self):
    json_data = json.loads(self._data.to_json(orient='records'))
    return data_to_asp(json_data)

  def build(self):
    if (self._strict):
      return self._spec()
    else:
      spec = self._spec()
      schema = self._schema()
      asp = cql2asp(spec) + schema
      result = run_draco(asp)
      return result

  def _is_partial(self):
    return (
      not self._strict or
      self._encoding_partial() and
      self._mark_partial()
    )
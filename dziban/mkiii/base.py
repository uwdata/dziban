from json import loads as json_parse
from copy import deepcopy
from draco.js import data2schema, schema2asp
from .encoding import Encoding

class Base:
  def __init__(self, data):
    self._data = data

    json_data = json_parse(data.to_json(orient='records'))
    self._schema = data2schema(json_data)
    self._encodings = { field : Encoding(field) for field in self._schema['stats'].keys() }

    self._fields = list(self._encodings.keys())
    self._selectedfields = set()
    self._anchor = None

  def clone(self):
    return deepcopy(self)
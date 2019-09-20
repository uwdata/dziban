from json import loads as json_parse
from copy import deepcopy
from draco.js import data2schema, schema2asp
from .encoding import Encoding

class Base:
  def __init__(self, data):
    self._data = data

    json_data = json_parse(data.to_json(orient='records'))
    self._schema = data2schema(json_data)
    self._encodings = []

    self._fields = list(self._schema['stats'].keys())
    self._anchor = None
    self._sol = None
    self._solved = False

  def data(self, data):
    clone = self.clone()

    clone._data = data

    json_data = json_parse(data.to_json(orient='records'))
    clone._schema = data2schema(json_data)

    clone._fields = list(self._schema['stats'].keys()) 
    return clone

  def clone(self):
    clone = deepcopy(self)
    clone._sol = None
    clone._solved = False

    return clone

  def _set_sol(self, sol):
    clone = self.clone()
    clone._sol = sol
    clone._solved = True

    return clone

  def _update_encodings(self, key, values, props):
    if ('aggregate', 'count') in props.items():
      count_enc = Encoding(aggregate='count')
      self._encodings.append(count_enc)
      props.pop('aggregate')
    
    if ('aggregate', None) in props.items():
      none_agg_enc = Encoding(aggregate=None)
      self._encodings.append(none_agg_enc)
      props.pop('aggregate')

      self._encodings = filter(lambda e : not (e._condition[0] == 'aggregate' and e._condition[1] == 'count'), self._encodings)

    for v in values:
      enc = Encoding(**{ key: v } )

      for k, v in props.items():
        getattr(enc, k)(v)

      self._encodings.append(enc)
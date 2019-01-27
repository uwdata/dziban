class VizEncoding:
  def __init__(self):
    self._encoding = {}
    self._encoding_wild = []
    
  def encoding(
    self,
    *argv,
    x=None,
    y=None,
    x2=None,
    y2=None,
    longtitude=None,
    latitude=None,
    color=None,
    opacity=None,
    fillOpacity=None,
    strokeOpacity=None,
    strokeWidth=None,
    size=None,
    shape=None,
    text=None,
    tooltip=None,
    href=None,
    key=None,
    order=None,
    detail=None,
    row=None,
    column=None,
  ):
    self._encoding = {
      'x': x,
      'y': y,
      'x2': x2,
      'y2': y2,
      'longtitude': longtitude,
      'latitude': latitude,
      'color': color,
      'opacity': opacity,
      'fillOpacity': fillOpacity,
      'strokeOpacity': strokeOpacity,
      'strokeWidth': strokeWidth,
      'size': size,
      'shape': shape,
      'text': text,
      'tooltip': tooltip,
      'href': href,
      'key': key,
      'order': order,
      'detail': detail,
      'row': row,
      'column': column
    }

    self._encoding_wild = argv

    return self

  def _encoding_partial(self):
    return len(self._encoding_wild) != 0

  def build_encoding(self):
    if (self._is_partial()):
      # compassql
      encodings = []
      for channel, enc in self._encoding.items():
        if (enc is not None):
          encodings.append({
            'channel': channel,
            **enc
          })

      for field in self._encoding_wild:
        encodings.append({
          'channel': '?',
          'field': field,
        })

      return { 'encodings': encodings }
    else:
      # vegalite
      encoding = {}
      for channel, enc in self._encoding.items():
        if (enc is not None):
          encoding[channel] = enc
    return { 'encoding': encoding }
class VizEncoding:
  def encoding(
    self,
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
    *argv
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

  def build_encoding(self):
    encoding = {}
    for channel, enc in self._encoding.items():
      if (enc is not None):
        encoding[channel] = enc
    return encoding
class VizMark:
  def __init__(self):
    self._mark = None
    
  def mark_area(self):
    self._mark = 'area'
    return self

  def mark_bar(self):
    self._mark = 'bar'
    return self

  def mark_circle(self):
    self._mark = 'circle'
    return self

  def mark_line(self):
    self._mark = 'line'
    return self

  def mark_point(self):
    self._mark = 'point'
    return self

  def mark_rect(self):
    self._mark = 'rect'
    return self

  def mark_rule(self):
    self._mark = 'rule'
    return self

  def mark_square(self):
    self._mark = 'square'
    return self

  def mark_text(self):
    self._mark = 'text'
    return self

  def mark_tick(self):
    self._mark = 'tick'
    return self

  def mark_geoshape(self):
    self._mark = 'geoshape'
    return self

  def _mark_partial(self):
    return self._mark is None

  def build_mark(self):
    if (self._mark):
      return { 'mark': self._mark }
    else:
      return { 'mark': '?' }

from typing import List

from dziban.mark import VizMark
from dziban.encoding import VizEncoding

class Viz(VizMark, VizEncoding):
  def __init__(self):
    return

  def build(self):
    return {
      'mark': self.build_mark(),
      'encoding': self.build_encoding()
    }
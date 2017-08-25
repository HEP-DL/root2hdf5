

class BaseMetadata(object):
  def __init__(self):
    self.children = []

  @property
  def is_leaf(self):
    return len(self.children) == 0

  @property
  def is_branch(self):
    return not self.is_leaf

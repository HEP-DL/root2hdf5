import progressbar
import logging


class BaseData(object):
  tree_name=''
  logger = logging.getLogger('root2hdf5.data_types.base')
  def __init__(self, _file):
    self.event_index=0
    self.chain = TChain(self.tree_name)
    self.chain.AddFile(_file)

  def convert(self):
    self.logger.info("Starting Conversion of: {}".format(self.tree_name))
    bar = progressbar.ProgressBar(maxval=self.chain.GetEntries(),
      widgets=[progressbar.Bar('=', '    [', ']'), ' ', 
                               progressbar.Percentage()])
    bar.start()
    for i in self:
      bar.update(i)
    bar.finish()
    self.logger.info("Done.")

  def __iter__(self):
    return self

  def __next__(self):
    return self.next()

  def next(self):
    if self.event_index == self.chain.GetEntries():
      raise StopIteration()
    self.chain.GetEntry(self.event_index)
    branch = getattr(self.chain, self.tree_name.replace('tree','branch'))
    self.process_branch(branch)
    return self.event_index
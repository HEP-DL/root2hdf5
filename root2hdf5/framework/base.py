
import logging
import h5py
import tqdm

class BaseFile(object):
  logger = logging.getLogger('root2hdf5.framework.base.BaseFile')

  def __init__(self, files=None):
    self._files = files if files is not None else []
    self._data_types = []

  @property
  def files(self):
    return self._files

  @property 
  def data_types(self):
    return self._data_types

  @property
  def conversions(self):
    return [i(self._file, self.output_file) for i in self.data_types ]

  def go(self):
    for _file in self.files:
      self.logger.info("Processing File: {}".format(_file))
      self._file = _file
      self.output_file = h5py.File(_file.replace('.root','.h5'),'w')
      for conv in self.conversions:
        conv.convert()


class BaseData(object):
  tree_name=''
  logger = logging.getLogger('root2hdf5.data_types.base')
  def __init__(self, _file):
    from ROOT import TChain
    self.event_index = 0
    self.chain = TChain(self.tree_name)
    self.chain.AddFile(_file)

  def convert(self):
    self.logger.info("Starting Conversion of: {}".format(self.tree_name))
    pbar = tqdm.tqdm(total=self.chain.GetEntries())
    for i in self:
      pbar.update(1)
    pbar.close()
    del pbar
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
    self.event_index += 1
    return self.event_index
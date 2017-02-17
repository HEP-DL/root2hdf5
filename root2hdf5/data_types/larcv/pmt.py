from root2hdf5.data_types.base import BaseData
import numpy as np
import logging

class PMTData(BaseData):
  logger = logging.getLogger('root2hdf5.data_types.pmt')
  tree_name = 'image2d_pmt_tree'

  def __init__(self, _file, output_file):
    super(PMTData, self).__init__(_file)
    from larcv import larcv
    self.array_converter = larcv.as_ndarray
    self.dataset = output_file.create_dataset("image2d/pmt", (10,1,1500,32), maxshape=(None,1,1500,32),
                                             chunks=(10,1,1500,32), dtype='f',compression="gzip")
    self.dataset.attrs['name'] = 'image2d_pmt'
    self.dataset.attrs['index0_name'] = 'eventN'
    self.dataset.attrs['index1_name'] = 'layerN'
    self.dataset.attrs['index3_name'] = 'pixelX'
    self.dataset.attrs['index4_name'] = 'pixelY'
    self.logger.info("Setting Up PMT Data Stream")
    self.buffer = np.ndarray((10,1,1500,32), dtype='H')
    self.buffer_index=0

  def process_branch(self, branch):
    layerimage = self.array_converter(branch.at(0))
    layerimage.resize(1500,32)
    self.buffer[self.buffer_index, 0] = layerimage
    self.buffer_index+=1
    if self.event_index %10==0:
      self.buffer_index=0
      self.dataset.resize( (self.event_index+10,1,1500,32) )
      self.dataset[self.event_index:self.event_index+10,:,:,:] = self.buffer

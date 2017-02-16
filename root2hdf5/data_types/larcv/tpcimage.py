import logging
from root2hdf5.data_types.base import BaseData
import numpy as np
from larcv import larcv

class TPCImage(BaseData):
  logger = logging.getLogger('root2hdf5.data_types.tpcimage')
  tree_name = 'image2d_tpc_hires_crop_tree'

  def __init__(self, _file, output_file):
    super(TPCImage, self).__init__(_file)
    self.logger.info("Setting Up TPC Data Stream")
    self.dataset = None
    self.dataset = output_file.create_dataset("image2d/tpc",
                                              (10,3,576,576),
                                                maxshape=(None,3,576,576),
                                                chunks=(10,3,576,576),
                                                dtype='f',compression="gzip")
    self.dataset.attrs['name']        = 'image2d_tpc_hires_crop'
    self.dataset.attrs['index0_name'] = 'eventN'
    self.dataset.attrs['index1_name'] = 'layerN'
    self.dataset.attrs['index3_name'] = 'pixelX'
    self.dataset.attrs['index4_name'] = 'pixelY'

    self.buffer = np.ndarray((10,3,576,576), dtype='f')
    self.buffer_index = 0


  def process_branch(self, branch):
    for layer in range(3):
      layerimage = larcv.as_ndarray(branch.at(layer))
      layerimage.resize(576,576)
      self.buffer[self.buffer_index, layer] = layerimage
    self.buffer_index+=1
    if self.event_index %10==0:
      self.buffer_index=0
      self.dataset.resize( (self.event_index+10,3,576,576) )
      self.dataset[self.event_index:self.event_index+10,:,:,:] = self.buffer
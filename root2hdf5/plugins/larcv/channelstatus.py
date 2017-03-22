import logging
from root2hdf5.data_types.base import BaseData
import numpy as np


class ChannelStatusData(BaseData):
  logger = logging.getLogger('root2hdf5.data_types.channelstatus')
  tree_name = 'chstatus_tpc_tree'

  def __init__(self, _file, output_file):
    super(ChannelStatusData, self).__init__(_file)
    self.logger.info("Setting Up Channel Status Data Stream")
    self.dataset = output_file.create_dataset("chstatus/tpc",
                                                        (10,3,2400),
                                                        maxshape=(None,3,2400),
                                                        chunks=(10,3,2400),
                                                        dtype='f',compression="gzip")
    self.dataset.attrs['name'] = 'chstatus_tpc'
    self.dataset.attrs['index0_name'] = 'eventN'
    self.dataset.attrs['index1_name'] = 'layerN'
    self.dataset.attrs['index3_name'] = 'wireN'

  def process_branch(self, branch):
    buff = np.ndarray( (3,2400), dtype='H')
    for plane in range(3):
      for index, status in enumerate(branch.Status(0).as_vector()):
        buff[branch.Status(plane).Plane(), index] = status
    self.dataset.resize((self.event_index+1, 3,2400))
    self.dataset[self.event_index,:,:] = buff
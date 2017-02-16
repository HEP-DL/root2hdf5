import logging
import h5py
import os

class LArCVFile(object):
  
  def __init__(self, files=None):
    self._files=files if files is not None else []
    self._data_types=[]

  @property
  def files(self):
    return self._files

  @property 
  def data_types(self):
    return self._data_types=[]

  def setup(self):
    if len(self.data_types) == 0:
      from root2hdf5.data_types.larcv import (TPCImage, ROIData, 
                                              PMTData, ChannelStatusData)
      self.data_types.append(TPCImage)    
      self.data_types.append(ROIData)
      self.data_types.append(PMTData)
      self.data_types.append(ChannelStatusData)

  def go(self):
    for _file in self.files():
      self.logger.info("Processing File: {}".format(_file))
      output_file = h5py.File(_file.replace('.root','.h5'),'w')
      conversions = [i(_file, output_file) for i in self.data_types ]
      for conv in conversion:
        conv.convert()


import logging
from root2hdf5.data_types.base import BaseData
import numpy as np
import os


class ROIConversion:
  def __init__(self, output_file, label='', method_name='', size=10):
    self.dataset = output_file.create_dataset('labels/{}'.format(label),
                                              (10,size,),
                                              maxshape=(None,size),
                                              chunks=(10,size),
                                              dtype='H',
                                              compression='gzip'
                                             )

    self.dataset.attrs['index0'] = "eventN"
    self.dataset.attrs['index1'] = 'index'
    self.buffer = np.ndarray( (10,size) )
    self.current_index=0
    self.method_name = method_name

  def fill_buffer(self, event_index, roi_index, roi):
    self.buffer[self.current_index, getattr(roi, self.method_name)() ] += 1 
    self.current_index +=1
    if self.current_index == 10:
      self.dataset.resize((event_index+10, self.buffer.shape[1]))
      self.dataset[event_index:event_index+10,:] = self.buffer
      self.current_index=0
      self.buffer = np.zeros(shape = self.buffer.shape)

  def finish(self):
    self.dataset.resize((self.dataset.shape[0]+self.current_index, self.buffer.shape[1]))
    self.dataset[event_index:event_index+self.current_index,:] = self.buffer


class CoordinateConversion:

  def __init__(self, output_file, label='', method_names=['','','']):
    self.dataset = output_file.create_dataset('labels/{}'.format(label),
                                              (10,1,3),
                                              maxshape=(None,None,3),
                                              chunks=(10,1,3),
                                              dtype='f',
                                              compression='gzip'
                                             )

    self.dataset.attrs['index0_name'] = "eventN"
    self.dataset.attrs['index1_name'] = 'index'
    self.dataset.attrs['index3_name'] = 'coordinate'
    self.buffer = np.ndarray( (10,1,3) )
    self.current_index=0
    self.method_names = method_names

  def fill_buffer(self, event_index, roi_index, roi):
    #resize the  if necessary
    if roi_index>=self.buffer.shape[1]:
      self.buffer.resize( (10,roi_index+1,3) )

    self.buffer[self.current_index, roi_index,:] = [getattr(roi, i)() for i in self.method_names]
    self.current_index +=1
    if self.current_index == 10:
      #then buffer is filled, let's dump this to file
      self.dataset.resize((event_index+10, self.buffer.shape[1],3))
      self.dataset[event_index:event_index+10,:,:] = self.buffer
      self.current_index=0
      self.buffer = np.zeros(shape = self.buffer.shape)

  def finish(self):
    self.dataset.resize((self.dataset.shape[0]+self.current_index, self.buffer.shape[1],3))
    self.dataset[event_index:event_index+self.current_index,:,:] = self.buffer


class BoundingBoxConversion:

  def __init__(self, output_file, label=''):
    self.dataset = output_file.create_dataset('labels/boundingBox',(10,1,1,4), maxshape=(None,None,None,4),
                                                 chunks=(10,1,1,4),dtype='f',compression='gzip')
    self.dataset.attrs['index0_name']='eventN'
    self.dataset.attrs['index1_name']='index'
    self.dataset.attrs['index2_name']='bbIndex'
    self.dataset.attrs['index3_name']='coordinate'
    self.buffer = np.ndarray( (10,1,1,4) )
    self.current_index=0

  def fill_buffer(self, event_index, roi_index, roi):
    #resize the  if necessary
    if roi_index>=self.buffer.shape[1]:
      self.buffer.resize( (10,roi_index+1,self.buffer.shape[2], 4) )

    if roi.BB().size()>= self.buffer.shape[2]:
      self.buffer.resize((10,self.buffer.shape[1], roi.BB().size(),4))

    for i in range(roi.BB().size()):
      self.buffer[self.current_index, roi_index,i,0]=roi.BB().at(long(i)).min_x()
      self.buffer[self.current_index, roi_index,i,1]=roi.BB().at(long(i)).min_y()
      self.buffer[self.current_index, roi_index,i,2]=roi.BB().at(long(i)).max_x()
      self.buffer[self.current_index, roi_index,i,3]=roi.BB().at(long(i)).max_x()

    self.current_index +=1
    if self.current_index == 10:
      #then buffer is filled, let's dump this to file
      self.dataset.resize((event_index+10, self.buffer.shape[1], self.buffer.shape[2],4))
      self.dataset[event_index:event_index+10,:,:,:] = self.buffer
      self.current_index=0
      self.buffer = np.zeros(shape = self.buffer.shape)

  def finish(self):
    self.dataset.resize((self.dataset.shape[0]+self.current_index, self.buffer.shape[1],self.buffer.shape[2], self.buffer.shape[3]))
    self.dataset[event_index:event_index+self.current_index,:,:,:] = self.buffer


class ROIData(BaseData):
  logger = logging.getLogger('root2hdf5.data_types.roidata')
  tree_name = 'partroi_tpc_hires_crop_tree'

  def __init__(self, _file, output_file):
    super(ROIData, self).__init__(_file)

    self.simple_conversions = [
      ROIConversion(output_file, 'type','Type',10),
      ROIConversion(output_file, 'shape','Shape', 3),
      CoordinateConversion(output_file, 'position', ['X','Y','Z']),
      CoordinateConversion(output_file, 'momentum', ['Px','Py','Pz']),
      CoordinateConversion(output_file, 'parentPosition', ['ParentX','ParentY','ParentZ']),
      CoordinateConversion(output_file, 'parentMomentum', ['ParentPx','ParentPy','ParentPz']),
      BoundingBoxConversion(output_file, 'boundingBox'),
    ]

    self.logger.info("Setting Up TPC Data Stream")
    self.event_index=0

  def process_branch(self, branch):
    roi_index=0
    for roi in branch.ROIArray():
      for conversion in self.simple_conversions:
        conversion.fill_buffer(self.event_index, roi_index, roi)
      roi_index+=1
    [conversion.finish for conversion in self.simple_conversions]

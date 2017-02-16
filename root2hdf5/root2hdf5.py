# -*- coding: utf-8 -*-


import h5py
import os, sys
from larcv import larcv
from ROOT import TChain
import numpy as np
from itertools import product
import progressbar



def convert_images(_file, output_file):
  pixel_tree_name = 'image2d_tpc_hires_crop_tree'
  pixel_ch = TChain(pixel_tree_name)
  pixel_ch.AddFile(os.path.join('dl',_file))

  image2d_tpc_hires_crop = output_file.create_dataset("image2d/tpc",
                                                      (10,3,576,576),
                                                      maxshape=(None,3,576,576),
                                                      chunks=(10,3,576,576),
                                                      dtype='f',compression="gzip")
  image2d_tpc_hires_crop.attrs['name'] = 'image2d_tpc_hires_crop'
  image2d_tpc_hires_crop.attrs['index0_name'] = 'eventN'
  image2d_tpc_hires_crop.attrs['index1_name'] = 'layerN'
  image2d_tpc_hires_crop.attrs['index3_name'] = 'pixelX'
  image2d_tpc_hires_crop.attrs['index4_name'] = 'pixelY'
  buff = np.ndarray((10,3,576,576), dtype='f')
  buff_index=0
  print "  Working on TPC Data"
  bar = progressbar.ProgressBar(maxval=pixel_ch.GetEntries(),
    widgets=[progressbar.Bar('=', '    [', ']'), ' ', progressbar.Percentage()])
  bar.start()
  for event in range(pixel_ch.GetEntries()):
    bar.update(event)

    pixel_ch.GetEntry(event)
    pixel_br=getattr(pixel_ch, pixel_tree_name.replace('tree','branch'))
    for layer in range(3):
      layerimage = larcv.as_ndarray(pixel_br.at(layer))
      layerimage.resize(576,576)
      buff[buff_index, layer] = layerimage
    buff_index+=1
    if event %10==0:
      buff_index=0
      image2d_tpc_hires_crop.resize( (event+10,3,576,576) )
      image2d_tpc_hires_crop[event:event+10,:,:,:] = buff
  bar.finish()

class ROIConversion:
  def __init__(self, output_file, label='', method_name=''):
    self.dataset = output_file.create_dataset('labels/{}'.format(label),
                                              (10,1,),
                                              maxshape=(None,None),
                                              chunks=(10,1),
                                              dtype='f',
                                              compression='gzip'
                                             )

    self.dataset.attrs['index0'] = "eventN"
    self.dataset.attrs['index1'] = 'index'
    self.buffer = np.ndarray( (10,1) )
    self.current_index=0
    self.method_name = method_name

  def fill_buffer(self, event_index, roi_index, roi):
    #resize the  if necessary
    if roi_index>=self.buffer.shape[1]:
      self.buffer.resize( (10,roi_index+1) )

    self.buffer[self.current_index, roi_index] = getattr(roi, self.method_name)()
    self.current_index +=1
    if self.current_index == 10:
      #then buffer is filled, let's dump this to file
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


def convert_roi(_file, output_file):
  print "  Working on ROI"
  roi_tree_name='partroi_tpc_hires_crop_tree'
  roi_br_name=roi_tree_name.replace('tree','branch')
  roi_ch = TChain(roi_tree_name)
  roi_ch.AddFile(os.path.join('dl',_file))


  simple_conversions = [
    ROIConversion(output_file, 'type','Type'),
    ROIConversion(output_file, 'shape','Shape'),
    ROIConversion(output_file, 'mcstIndex','MCSTIndex'),
    ROIConversion(output_file, 'mctIndex','MCTIndex'),
    ROIConversion(output_file, 'energyDeposited','EnergyDeposit'),
    ROIConversion(output_file, 'energyInitial','EnergyInit'),
    ROIConversion(output_file, 'pdgCode','PdgCode'),
    ROIConversion(output_file, 'parentPDGCode','ParentPdgCode'),
    ROIConversion(output_file, 'trackID','TrackID'),
    ROIConversion(output_file, 'parentTrackID','ParentTrackID'),
    ROIConversion(output_file, 'neutrinoInteractionType','NuInteractionType'),
    ROIConversion(output_file, 'neutrinoCurrentType','NuCurrentType'),
    CoordinateConversion(output_file, 'position', ['X','Y','Z']),
    CoordinateConversion(output_file, 'momentum', ['Px','Py','Pz']),
    CoordinateConversion(output_file, 'parentPosition', ['ParentX','ParentY','ParentZ']),
    CoordinateConversion(output_file, 'parentMomentum', ['ParentPx','ParentPy','ParentPz']),
    BoundingBoxConversion(output_file, 'boundingBox'),
  ]

  bar = progressbar.ProgressBar(maxval=roi_ch.GetEntries(),
    widgets=[progressbar.Bar('=', '    [', ']'), ' ', progressbar.Percentage()])
  bar.start()
  
  for roi_array in range(roi_ch.GetEntries()):
    bar.update(roi_array)

    roi_ch.GetEntry(roi_array)
    roi_index=0
    for roi in getattr(roi_ch, roi_tree_name.replace('tree','branch')).ROIArray():

      for conversion in simple_conversions:
        conversion.fill_buffer(roi_array, roi_index, roi)

      roi_index+=1
  [conversion.finish for conversion in simple_conversions]
  bar.finish()

def convert_pmt(_file, output_file):
  print "  Working on PMT Data"
  pmt_tree_name='image2d_pmt_tree'
  pmt_br_name=pmt_tree_name.replace('tree','branch')
  pmt_ch = TChain(pmt_tree_name)
  pmt_ch.AddFile(os.path.join('dl',_file))

  image2d_pmt = output_file.create_dataset("image2d/pmt", (10,1,1500,32), maxshape=(None,1,1500,32),
                                           chunks=(10,1,1500,32), dtype='f',compression="gzip")
  image2d_pmt.attrs['name'] = 'image2d_pmt'
  image2d_pmt.attrs['index0_name'] = 'eventN'
  image2d_pmt.attrs['index1_name'] = 'layerN'
  image2d_pmt.attrs['index3_name'] = 'pixelX'
  image2d_pmt.attrs['index4_name'] = 'pixelY'
  buff = np.ndarray((10,1,1500,32), dtype='H')
  buff_index=0
  bar = progressbar.ProgressBar(maxval=pmt_ch.GetEntries(),
    widgets=[progressbar.Bar('=', '    [', ']'), ' ', progressbar.Percentage()])
  bar.start() 
  for event in range(pmt_ch.GetEntries()):
    bar.update(event)

    pmt_ch.GetEntry(event)
    pmt_br=getattr(pmt_ch, pmt_tree_name.replace('tree','branch'))
    layerimage = larcv.as_ndarray(pmt_br.at(0))
    layerimage.resize(1500,32)
    buff[buff_index, 0] = layerimage
    buff_index+=1
    if event %10==0:
      buff_index=0
      image2d_pmt.resize( (event+10,1,1500,32) )
      image2d_pmt[event:event+10,:,:,:] = buff

  bar.finish()

def convert_segment(_file, output_file):
  print "  Working on Segmentation Data"
  pixel_tree_name = 'image2d_segment_hires_crop_tree'
  pixel_ch = TChain(pixel_tree_name)
  pixel_ch.AddFile(os.path.join('dl',_file))

  image2d_tpc_hires_crop = output_file.create_dataset("image2d/segment",
                                                      (10,3,576,576),
                                                      maxshape=(None,3,576,576),
                                                      chunks=(10,3,576,576),
                                                      dtype='f',compression="gzip")
  image2d_tpc_hires_crop.attrs['name'] = 'image2d_segment_hires_crop_tree'
  image2d_tpc_hires_crop.attrs['index0_name'] = 'eventN'
  image2d_tpc_hires_crop.attrs['index1_name'] = 'layerN'
  image2d_tpc_hires_crop.attrs['index3_name'] = 'pixelX'
  image2d_tpc_hires_crop.attrs['index4_name'] = 'pixelY'
  buff = np.ndarray((10,3,576,576), dtype='H')
  buff_index=0
  bar = progressbar.ProgressBar(maxval=pixel_ch.GetEntries(),
    widgets=[progressbar.Bar('=', '    [', ']'), ' ', progressbar.Percentage()])
  bar.start()
  for event in range(pixel_ch.GetEntries()):
    bar.update(event)

    pixel_ch.GetEntry(event)
    pixel_br=getattr(pixel_ch, pixel_tree_name.replace('tree','branch'))
    for layer in range(3):
      layerimage = larcv.as_ndarray(pixel_br.at(layer))
      layerimage.resize(576,576)
      buff[buff_index, layer] = layerimage
    buff_index+=1
    if event %10==0:
      buff_index=0
      image2d_tpc_hires_crop.resize( (event+10,3,576,576) )
      image2d_tpc_hires_crop[event:event+10,:,:,:] = buff
  bar.finish()


def convert_chst(_file, output_file):

  print "  Working On Channel Status Information"

  ch_tree_name='chstatus_tpc_tree'
  ch_br_name=ch_tree_name.replace('tree','branch')
  ch_ch = TChain(ch_tree_name)
  ch_ch.AddFile(os.path.join('dl',_file))

  chstatus_tpc = output_file.create_dataset("chstatus/tpc",
                                                      (10,3,2400),
                                                      maxshape=(None,3,2400),
                                                      chunks=(10,3,2400),
                                                      dtype='f',compression="gzip")
  chstatus_tpc.attrs['name'] = 'chstatus_tpc_tree'
  chstatus_tpc.attrs['index0_name'] = 'eventN'
  chstatus_tpc.attrs['index1_name'] = 'layerN'
  chstatus_tpc.attrs['index3_name'] = 'wireN'
  bar = progressbar.ProgressBar(maxval=ch_ch.GetEntries(),
    widgets=[progressbar.Bar('=', '    [', ']'), ' ', progressbar.Percentage()])
  bar.start()
  for event in range(ch_ch.GetEntries()):
    bar.update(event)
    ch_ch.GetEntry(event)
    ch_br=getattr(ch_ch, ch_br_name)
    buff = np.ndarray( (3,2400), dtype='H')
    for plane in range(3):
      for index, status in enumerate(ch_br.Status(0).as_vector()):
        buff[ch_br.Status(plane).Plane(), index] = status
    chstatus_tpc.resize((event+1, 3,2400))
    chstatus_tpc[event,:,:] = buff
  bar.finish()

def convert_file(_file):
  print "Converting File: ", _file
  output_file = h5py.File(os.path.join("hdf5",_file.replace('.root','.h5')), "w")
  
  convert_images(_file, output_file)
  convert_roi(_file, output_file)
  convert_pmt(_file, output_file)
  convert_segment(_file, output_file)
  convert_chst(_file, output_file)

if __name__ == "__main__":
  files = os.listdir('./dl')
  exclude = []#['eminus_test.root']
  for _file in files:
    if _file in exclude:
      continue
    try:
      convert_file(_file)
    except Exception as e:
      print "COULD NOT CONVERT FILE: ",_file
      print e
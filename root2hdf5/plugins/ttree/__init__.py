
from root2hdf5.framework.base import BaseData, BaseFile
import ROOT
import numpy as np
import logging


class TTreeData(BaseData):
  logger = logging.getLogger('root2hdf5.ttree.ttree')
  
  def __init__(self, tree_name, branches, file_name,output_file):
    self.tree_name = tree_name
    self.branches = branches
    super(TTreeData, self).__init__(file_name)
    self.dataset = output_file.create_dataset(tree_name,
                                              (1,len(branches)),
                                              maxshape=(None,len(branches)),
                                              chunks=(1,len(branches)),
                                              dtype='f', compression="gzip")
    for index, branch in enumerate(branches):
      self.dataset.attrs['index{}_name'.format(index)]=branch

  def process_tree(self):
    buff = np.ndarray( (1,len(self.branches)) ,'f')
    for index, branch in enumerate(self.branches):
      try:
        value = float(getattr(self.chain, branch))
        buff[0,index] = value
      except:
        branch_name = branch.split('[')[0]
        tbranch = getattr(self.chain, branch_name)
        for index, item in enumerate(tbranch):
          new_name = branch_name+"[{}]".format(index)
          buff[0,self.branches.index(new_name)] = item
    self.dataset.resize((self.event_index+1, len(self.branches)))
    self.dataset[self.event_index,:] = buff

  def next(self):
    if self.event_index == self.chain.GetEntries():
      raise StopIteration()
    self.chain.GetEntry(self.event_index)
    self.process_tree()
    self.event_index+=1
    return self.event_index


class TFileConversion(BaseFile):
  logger = logging.getLogger('root2hdf5.ttree.tfile')  

  def __init__(self, _file):
    super(TFileConversion, self).__init__(_file)
    self.tree_branches = {}

  def add_tree_branch(self, tree,branch):
    for ttree in self.tree_branches:
      if tree == ttree and branch in self.tree_branches[tree]:
        return False
    if not tree in self.tree_branches:
      self.logger.info("Adding tree: {} to conversions".format(tree))
      self.tree_branches[tree]=[]
    self.tree_branches[tree].append(branch)
    return True

  @property
  def conversions(self):
    return [TTreeData(tree, self.tree_branches[tree], 
            self._file, self.output_file) for tree in self.tree_branches]


def process(file_names):
  logger = logging.getLogger()
  converter = TFileConversion(file_names)
  for _file in file_names:
    tfile = ROOT.TFile(_file,"READ")
    trees = [i.GetName() for i in tfile.GetListOfKeys()]
    for tree in trees:
      ttree = tfile.Get(tree)
      branches = []
      for branch in ttree.GetListOfBranches():
        try:
          value = float( getattr(ttree, branch.GetName() ) )
          branches.append(branch.GetName() )
        except Exception as e:
          logger.warning("Found NTuple instead of value for: "+branch.GetName())
          for index, value in enumerate(getattr(ttree, branch.GetName())):
            branches.append(branch.GetName()+"[{}]".format(index))
      for branch in branches:
        converter.add_tree_branch(tree,branch)
  converter.go()
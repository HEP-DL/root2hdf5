
from root2hdf5.framework.base import BaseData, BaseFile
import ROOT
import numpy as np


class TTreeData(BaseData):
  
  def __init__(self, tree_name, branches, file_name,output_file):
    self.tree_name = tree_name
    self.branches = branches
    super(TTreeData, self).__init__(file_name)
    self.dataset = output_file.create_dataset(tree_name,
                                                        (1,len(branches)),
                                                        maxshape=(None,len(branches)),
                                                        chunks=(1,len(branches)),
                                                        dtype='f',compression="gzip")
    for index, branch in enumerate(branches):
      self.dataset.attrs['index{}_name'.format(index)]=branch

  def process_tree(self, branches):
    buff = np.ndarray( (1,len(branches)) ,'f')
    self.dataset.resize((self.event_index+1, len(branches)))
    self.dataset[self.event_index] = buff

  def next(self):
    if self.event_index == self.chain.GetEntries():
      raise StopIteration()
    self.chain.GetEntry(self.event_index)
    branch_values = [getattr(self.chain, i) for i in self.branches]
    self.process_tree(branch_values)
    self.event_index+=1
    return self.event_index

class TFileConversion(BaseFile):
  
  def __init__(self, _file):
    super(TFileConversion, self).__init__(_file)
    self.tree_branches = {}

  def add_tree_branch(self, tree,branch):
    for ttree in self.tree_branches:
      if tree == ttree and branch in self.tree_branches[tree]:
        return

    if not tree in self.tree_branches:
      self.tree_branches[tree]=[]
    self.tree_branches[tree].append(branch)

  @property
  def conversions(self):
    output=[]
    for tree in self.tree_branches:
        output.append(TTreeData(tree, self.tree_branches[tree], 
                                  self._file, self.output_file))
    return output


def process(file_names):
  converter = TFileConversion(file_names)

  for _file in file_names:
    tfile = ROOT.TFile(_file,"READ")
    trees = [i.GetName() for i in tfile.GetListOfKeys()]

    for tree in trees:
      ttree = tfile.Get(tree)
      branches = [i.GetName() for i in ttree.GetListOfBranches() ]
      for branch in branches:
        converter.add_tree_branch(tree,branch)

  converter.go()
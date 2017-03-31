# ROOT2HDF5

[![Updates](https://pyup.io/repos/github/hep-dl/root2hdf5/shield.svg)](https://pyup.io/repos/github/hep-dl/root2hdf5/)
[![Python 3](https://pyup.io/repos/github/hep-dl/root2hdf5/python-3-shield.svg)](https://pyup.io/repos/github/hep-dl/root2hdf5/)
[![Build Status](https://travis-ci.org/HEP-DL/root2hdf5.svg?branch=master)](https://travis-ci.org/HEP-DL/root2hdf5)
[![Documentation Status](https://readthedocs.org/projects/root2hdf5/badge/?version=latest)](https://root2hdf5.readthedocs.io/en/latest/?badge=latest)


A Very Non-Generic ROOT File to HDF5 Converter


* Free software: GNU General Public License v3
* Documentation: https://root2hdf5.readthedocs.io.


## Features


Currently, this conversion only supports: 

* LArCV ROOT files to HDF5.

  > NOTE: This requires both `ROOT` and `LArCV` to be installed. These are not managed by `pip`, and thus are not collected in `requirements.txt`.

* ROOT Files with flat TTrees

    * This assumes that data is stored in trees in the parent directory. The trees themselves must contain primitives or ntuples in the branches.


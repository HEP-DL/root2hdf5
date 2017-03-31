# Installation

There are several options for deploying this software.

## Installing pre-requisites

The one major pre-requisite that needs to be installed is ROOT. Instructions can be found [here](https://root.cern.ch/downloading-root).

Bear in mind that the 

### Plugins

For LArCV files to HDF5 conversion, LArCV will need to be installed. Instructions can be found [here](https://github.com/LArbys/LArCV).




## Using pip

Pip can be used to install the package from github

~~~ bash
pip install git+https://http://github.com/HEP-DL/root2hdf5
~~~

## Using Distutils

Similarly, the source code can be cloned and installed directly

~~~ bash
git clone https://http://github.com/HEP-DL/root2hdf5
cd root2hdf5
python setup.py install
~~~
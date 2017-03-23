#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import setup, find_packages
from pip.req import parse_requirements
import pip

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

install_reqs = reqs = [str(ir.req) for ir in parse_requirements('requirements.txt',
    session=pip.download.PipSession())]
dev_reqs = [str(ir.req) for ir in parse_requirements('requirements_dev.txt',
    session=pip.download.PipSession())]

setup(
    name='root2hdf5',
    version='1.1.3',
    description="A Very Non-Generic ROOT File to HDF5 Converter",
    long_description=readme + '\n\n' + history,
    author="Kevin Wierman",
    author_email='kevin.wierman@pnnl.gov',
    url='https://github.com/HEP-DL/root2hdf5',
    packages=find_packages(),
    package_dir={'root2hdf5':
                 'root2hdf5'},
    entry_points={
        'console_scripts': [
            'root2hdf5=root2hdf5.cli:main'
        ],
        'root2hdf5.plugins':[
            'ttree=root2hdf5.plugins.ttree',
            'larcv=root2hdf5.plugins.larcv',
        ]
    },
    include_package_data=True,
    install_requires=install_reqs,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='root2hdf5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=dev_reqs
)

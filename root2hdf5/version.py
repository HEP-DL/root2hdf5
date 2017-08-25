"""
  Defines a check version for root. This should be run BEFORE
  trying to import ROOT so that the interpreter doesn't crash.
"""

import os
import sys
import logging
import subprocess
from . import assets

__root_macro_dir__ = os.path.dirname(assets.__file__)
__root_command__ = ['root','-l','-q','-b',
                    '{}/getPythonVersion.C'.format(__root_macro_dir__)]

err_msg = """ROOT was compiled against a different version of Python.
---------------------------------------------------------------------
  ROOT Python Version output:
{}
---------------------------------------------------------------------
  Current Python: 
{}
---------------------------------------------------------------------
  Please use the correct version of Python.
"""

def check_root_version():
  """
    Checks to see if ROOT exists and if it does, checks the version of
    python it was compiled against and whether or not it coincides with
    the current version

    :returns bool: True if root is accessible and the correct version
    :raises ImportError: When ROOT can be accessed

    TODO: This can be refined by
  """
  output = subprocess.check_output(__root_command__)
  if not sys.version in output:
    msg = err_msg.format(output, sys.version)
    raise ImportError(msg)
  return True

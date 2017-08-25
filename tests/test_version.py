

import unittest
import pytest


from root2hdf5 import cli



class TestVersion(unittest.TestCase):

    def test_basic_functionality(self):
        """
            There really is no good way to check
            this out without having access to the test
            system. Another reason to ditch ROOT.
        """
from unittest import TestCase
from nose.tools import *
from sparchive import mkstemppath
from os import path

class InitTest(TestCase):
    def test_mkstemppath(self):
        n = mkstemppath()
        assert_false(path.exists(n))

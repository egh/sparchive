import datetime
import time
from sparxive.filer import Filer
from unittest import TestCase
from nose.tools import assert_equal
import os

class FilerTest(TestCase):
    def test_find_file(self):
        filer = Filer('.')
        file = filer.find_file('foo')
        assert_equal(os.path.abspath(os.path.join('tests', 'fixtures', 'foobar', 'foo')), file)

    def test_get_mtime(self):
        filer = Filer('.')
        assert_equal(time.gmtime(1385192191), filer.get_mtime(os.path.join('tests', 'fixtures', 'foobar')))
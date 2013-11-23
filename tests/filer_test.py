import datetime
import time
from sparxive.filer import Filer
from unittest import TestCase
from nose.tools import assert_equal
import os
from os import path

class FilerTest(TestCase):
    def test_find_file(self):
        filer = Filer('.')
        assert_equal(path.abspath(path.join('tests', 'fixtures', 'foobar', 'foo')), filer.find_file('foo'))
        assert_equal(None, filer.find_file("NONE"))

    def test_get_mtime(self):
        filer = Filer('.')
        assert_equal(time.gmtime(1385192191), filer.get_mtime(path.join('tests', 'fixtures', 'foobar')))
        
    def test_find_archive_path(self):
        filer = Filer('.')
        assert_equal(path.join('.', '2013','11','foobar.zip.rz'), filer.find_archive_path(path.join('tests', 'fixtures', 'foobar')))
import datetime
import time
from sparxive.filer import Filer
from unittest import TestCase
from nose.tools import assert_equal
import os
from os import path
from tempfile import mkdtemp

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
        assert_equal(path.join('.', '2013','11','foobar.zip.rz'), filer.find_archive(path.join('tests', 'fixtures', 'foobar')).archive_path)
        assert_equal(path.join('.', '2013','11','foo.zip.rz'), filer.find_archive(path.join('tests', 'fixtures', 'foobar', 'foo')).archive_path)
        # trailing slash check
        assert_equal(path.join('.', '2013','11','foobar.zip.rz'), filer.find_archive(path.join('tests/fixtures/foobar/')).archive_path)

    def test_file(self):
        olddir = os.getcwd()
        rootdir = mkdtemp()
        filer = Filer(rootdir)
        os.chdir(path.join('tests', 'fixtures'))
        results = filer.file('foobar')
        assert_equal(results[0], True)
        assert_equal(results[1], 0)
        assert(os.path.exists(os.path.join(rootdir, '2013', '11', 'foobar.zip.rz')))
        os.chdir(olddir)
import datetime
import time
from sparchive.archive import Archive
from sparchive.filer import Filer
from sparchive import rzip
from unittest import TestCase
from nose.tools import *
import os
from os import path
from tempfile import mkdtemp
from zipfile import ZipFile

class FilerTest(TestCase):
    def setUp(self):
        foo = path.join('tests', 'fixtures', 'foobar', 'foo')
        bar = path.join('tests', 'fixtures', 'foobar', 'bar')
        os.utime(foo, (978307200,  978307200))
        os.utime(bar, (978307200,  978307200))

    def test_find_file(self):
        filer = Filer('.', rzip)
        assert_equal(path.abspath(path.join('tests', 'fixtures', 'foobar', 'foo')), filer.find_file('foo'))
        assert_equal(None, filer.find_file("NONE"))

    def test_get_mtime(self):
        filer = Filer('.', rzip)
        assert_equal(time.gmtime(978307200), filer.get_mtime(path.join('tests', 'fixtures', 'foobar')))
        
    def test_find_archive_path(self):
        filer = Filer('.', rzip)
        assert_equal(path.join('.', '2001','01','foobar.zip.rz'), filer.find_archive(path.join('tests', 'fixtures', 'foobar')).archive_path)
        assert_equal(path.join('.', '2001','01','foo.zip.rz'), filer.find_archive(path.join('tests', 'fixtures', 'foobar', 'foo')).archive_path)
        # trailing slash check
        assert_equal(path.join('.', '2001','01','foobar.zip.rz'), filer.find_archive(path.join('tests/fixtures/foobar/')).archive_path)

    def test_file(self):
        olddir = os.getcwd()
        rootdir = mkdtemp()
        filer = Filer(rootdir, rzip)
        results = filer.file(path.join('tests', 'fixtures', 'foobar'))
        assert_equal(results[0], True)
        assert_equal(results[1], 0)
        assert(os.path.exists(os.path.join(rootdir, '2001', '01', 'foobar.zip.rz')))
        with rzip.TempUncompress(results[2].archive_path) as zippath:
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                for info in myzip.infolist():
                    assert_true(info.filename.startswith("versions/0/foobar"))

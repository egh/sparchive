import os
from sparxive import rzip
from sparxive.archive import Archive, get_mtime
from unittest import TestCase
from nose.tools import assert_equal
from sparxive import mkstemppath
from tempfile import mkdtemp
from zipfile import ZipFile
import time

class TestArchive(TestCase):
    def test_get_mtime(self):
        assert_equal(time.ctime(1385061271), get_mtime(os.path.join('tests', 'fixtures')))

    def test_add_file(self):
        foo = os.path.join('tests', 'fixtures', 'foo')
        bar = os.path.join('tests', 'fixtures', 'bar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version(foo)
        a.add_version(bar)
        with rzip.TempUnrzip(apath) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                filenames = []
                for info in myzip.infolist():
                    filenames.append(info.filename)
                assert_equal(filenames, ["0/tests/fixtures/foo", "1/tests/fixtures/bar"])

    def test_add_100_versions(self):
        foo = os.path.join('tests', 'fixtures', 'foo')
        apath = mkstemppath()
        a = Archive(apath)
        for n in range(0, 100):
            a.add_version(foo)
        with rzip.TempUnrzip(apath) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                filenames = []
                filenames_assert = [ "%d/tests/fixtures/foo"%(n) for n in range(0, 100) ]
                for info in myzip.infolist():
                    filenames.append(info.filename)
                assert_equal(filenames_assert, filenames)

    def test_extract_version(self):
        foo = os.path.join('tests', 'fixtures', 'foo')
        bar = os.path.join('tests', 'fixtures', 'bar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version(foo)
        a.add_version(bar)
        xdir = mkdtemp()
        a.extract_version(0, xdir)
        assert(os.path.exists(os.path.join(xdir, '0', 'tests', 'fixtures', 'foo')))
        assert_equal("hello, world", open(os.path.join(xdir, '0', 'tests', 'fixtures', 'foo')).read())

        a.extract_version(1, xdir)
        assert(os.path.exists(os.path.join(xdir, '1', 'tests', 'fixtures', 'bar')))
        assert_equal("goodbye, world", open(os.path.join(xdir, '1', 'tests', 'fixtures', 'bar')).read())

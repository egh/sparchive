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
    def assert_ziprz_filenames(self, path, filenames):
        with rzip.TempUnrzip(path) as zippath:
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                assert_equal(filenames, [ info.filename for info in myzip.infolist() ])
        
    def test_get_mtime(self):
        assert_equal(time.ctime(1385061271), get_mtime(os.path.join('tests', 'fixtures')))

    def test_add_file(self):
        foo = os.path.join('tests', 'fixtures', 'foo')
        bar = os.path.join('tests', 'fixtures', 'bar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_versions([foo, bar])
        self.assert_ziprz_filenames(apath, ["0/tests/fixtures/foo", "1/tests/fixtures/bar"])

    def test_add_100_versions(self):
        foo = os.path.join('tests', 'fixtures', 'foo')
        apath = mkstemppath()
        a = Archive(apath)
        for n in range(0, 100):
            a.add_version(foo)
        self.assert_ziprz_filenames(apath, [ "%d/tests/fixtures/foo"%(n) for n in range(0, 100) ])

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
        assert_equal(open(foo).read(), open(os.path.join(xdir, '0', 'tests', 'fixtures', 'foo')).read())

        a.extract_version(1, xdir)
        assert(os.path.exists(os.path.join(xdir, '1', 'tests', 'fixtures', 'bar')))
        assert_equal(open(bar).read(), open(os.path.join(xdir, '1', 'tests', 'fixtures', 'bar')).read())

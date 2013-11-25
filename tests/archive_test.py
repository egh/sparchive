# -*- coding: utf-8 -*-
import os
from sparxive import rzip
from sparxive.archive import Archive
from unittest import TestCase
from nose.tools import assert_equal
from sparxive import mkstemppath
from tempfile import mkdtemp
from zipfile import ZipFile
import time
import shutil

class TestArchive(TestCase):
    def setUp(self):
        os.chdir(os.path.join('tests', 'fixtures'))

    def tearDown(self):
        os.chdir(os.path.join('..', '..'))

    def assert_ziprz_filenames(self, path, filenames):
        with rzip.TempUnrzip(path) as zippath:
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                assert_equal(filenames, [ info.filename for info in myzip.infolist() ])

    def test_crc32(self):
        assert_equal('ffab723a', "%x"%(Archive._crc32(os.path.join('foobar', 'foo'))))

    def test_zip_versions(self):
        foo = os.path.join('foobar', 'foo')
        bar = os.path.join('foobar', 'bar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_versions([foo, bar])
        with rzip.TempUnrzip(apath) as zippath:
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                assert_equal([[('foobar/foo', 4289425978)], [('foobar/bar', 1226766874)]],
                             Archive._zip_versions(myzip))

    def test_has_version(self):
        foo = os.path.join('foobar', 'foo')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version(foo)
        assert_equal(0, a.has_version(foo))
        assert_equal(None, a.has_version(os.path.join('foobar', 'bar')))

    def test_has_version_dir(self):
        foo = os.path.join('foobar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version(foo)
        assert_equal(0, a.has_version(foo))
        assert_equal(None, a.has_version(os.path.join('foobar', 'bar')))
        assert_equal(None, a.has_version(os.getcwd()))

    def test_add_file(self):
        foo = os.path.join('foobar', 'foo')
        bar = os.path.join('foobar', 'bar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_versions([foo, bar])
        self.assert_ziprz_filenames(apath, ["0/foobar/foo", "1/foobar/bar"])

    def test_add_unicode_file(self):
        i = "“Iñtërnâtiônàlizætiøn”"
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version(i)
        self.assert_ziprz_filenames(apath, ["0/“Iñtërnâtiônàlizætiøn”"])
        xdir = mkdtemp()
        a.extract(xdir, 0)
        assert(os.path.exists(os.path.join(xdir, '0', "“Iñtërnâtiônàlizætiøn”")))
        assert_equal(open(i).read(), open(os.path.join(xdir, '0', '“Iñtërnâtiônàlizætiøn”')).read())

    def test_add_100_versions(self):
        foo = os.path.join('foobar', 'foo')
        apath = mkstemppath()
        a = Archive(apath)
        for n in range(0, 100):
            a.add_version(foo)
        self.assert_ziprz_filenames(apath, [ "%d/foobar/foo"%(n) for n in range(0, 100) ])

    def test_add_dir(self):
        dir = 'foobar'
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version(dir)
        self.assert_ziprz_filenames(apath, ["0/foobar/bar", "0/foobar/foo"])

    def test_extract(self):
        foo = os.path.join('foobar', 'foo')
        bar = os.path.join('foobar', 'bar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version(foo)
        a.add_version(bar)
        xdir = mkdtemp()
        a.extract(xdir, 0)
        assert(os.path.exists(os.path.join(xdir, '0', 'foobar', 'foo')))
        assert_equal(open(foo).read(), open(os.path.join(xdir, '0', 'foobar', 'foo')).read())
        
        a.extract(xdir, 1)
        assert(os.path.exists(os.path.join(xdir, '1', 'foobar', 'bar')))
        assert_equal(open(bar).read(), open(os.path.join(xdir, '1', 'foobar', 'bar')).read())
        shutil.rmtree(xdir)

        # now extract all versions
        xdir = mkdtemp()
        a.extract(xdir)
        assert(os.path.exists(os.path.join(xdir, '0', 'foobar', 'foo')))
        assert_equal(open(foo).read(), open(os.path.join(xdir, '0', 'foobar', 'foo')).read())
        assert(os.path.exists(os.path.join(xdir, '1', 'foobar', 'bar')))
        assert_equal(open(bar).read(), open(os.path.join(xdir, '1', 'foobar', 'bar')).read())
        shutil.rmtree(xdir)

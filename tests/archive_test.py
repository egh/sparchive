# -*- coding: utf-8 -*-
import struct
from datetime import datetime
import os
from sparchive import rzip
from sparchive.archive import Archive
from unittest import TestCase
from nose.tools import *
from sparchive import mkstemppath
from tempfile import mkdtemp
from zipfile import ZipFile, ZipInfo
import time
import shutil

class TestArchive(TestCase):
    def setUp(self):
        os.chdir(os.path.join('tests', 'fixtures'))

    def tearDown(self):
        os.chdir(os.path.join('..', '..'))

    @staticmethod
    def assert_ziprz_filenames(path, filenames):
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
        a.add_version([foo])
        a.add_version([bar])
        with rzip.TempUnrzip(apath) as zippath:
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                assert_equal([[('foobar/foo', 4289425978)], [('foobar/bar', 1226766874)]],
                             Archive._zip_versions(myzip))

    def test_has_version(self):
        foo = os.path.join('foobar', 'foo')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version([foo])
        assert_equal(0, a.has_version(foo))
        assert_equal(None, a.has_version(os.path.join('foobar', 'bar')))

    def test_has_version_dir(self):
        foo = os.path.join('foobar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version([foo])
        assert_equal(0, a.has_version(foo))
        assert_equal(None, a.has_version(os.path.join('foobar', 'bar')))
        assert_equal(None, a.has_version(os.getcwd()))

    def test_add_file(self):
        foo = os.path.join('foobar', 'foo')
        bar = os.path.join('foobar', 'bar')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version([foo])
        a.add_version([bar])
        TestArchive.assert_ziprz_filenames(apath, ["0/foobar/foo", "1/foobar/bar"])

    def test_add_unicode_file(self):
        i = "“Iñtërnâtiônàlizætiøn”"
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version([i])
        TestArchive.assert_ziprz_filenames(apath, ["0/“Iñtërnâtiônàlizætiøn”"])
        xdir = mkdtemp()
        a.extract(xdir, 0)
        assert(os.path.exists(os.path.join(xdir, '0', "“Iñtërnâtiônàlizætiøn”")))
        assert_equal(open(i).read(), open(os.path.join(xdir, '0', '“Iñtërnâtiônàlizætiøn”')).read())

    def test_add_100_versions(self):
        foo = os.path.join('foobar', 'foo')
        apath = mkstemppath()
        a = Archive(apath)
        for n in range(0, 100):
            a.add_version([foo])
        TestArchive.assert_ziprz_filenames(apath, [ "%d/foobar/foo"%(n) for n in range(0, 100) ])

    def test_add_dir(self):
        dir = 'foobar'
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version([dir])
        TestArchive.assert_ziprz_filenames(apath, ["0/foobar/", "0/foobar/bar", "0/foobar/foo"])

    def test_extract(self):
        foo = os.path.join('foobar', 'foo')
        bar = os.path.join('foobar', 'bar')
        os.utime(foo, (978307200,  978307200))
        os.utime(bar, (978307200,  978307200))
        os.chmod(foo, 0644)
        os.chmod(bar, 07755)
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version([foo])
        a.add_version([bar])
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
        assert_equal(978307200.0, os.path.getmtime(os.path.join(xdir, '0', 'foobar', 'foo')))
        assert_equal(0644, os.stat(os.path.join(xdir, '0', 'foobar', 'foo')).st_mode & 0000777)

        assert(os.path.exists(os.path.join(xdir, '1', 'foobar', 'bar')))
        assert_equal(978307200.0, os.path.getmtime(os.path.join(xdir, '1', 'foobar', 'bar')))
        assert_equal(open(bar).read(), open(os.path.join(xdir, '1', 'foobar', 'bar')).read())
        print oct(os.stat(os.path.join(xdir, '1', 'foobar', 'bar')).st_mode)
        assert_equal(07755, os.stat(os.path.join(xdir, '1', 'foobar', 'bar')).st_mode & 0007777)
        shutil.rmtree(xdir)

    def test_get_utc_mtime(self):
        apath = mkstemppath()
        with file(apath, 'a'):
            pass
        os.utime(apath, (978307200,  978307200)) # 1 Jan 2001, 00:00:00 UTC
        assert_equal(datetime(2001, 1, 1, 0, 0), Archive.get_mtime_as_utcdatetime(apath))
        os.unlink(apath)

    def test_unixtime_to_utcziptime(self):
        assert_equal(Archive.unixtime_to_utcziptime(978307200), (2001, 1, 1, 0, 0, 0))

    def test_parseextra(self):
        info = ZipInfo("foo")
        info.extra = struct.pack('<HHBl', 0x5455, 5, 1, 978307200)
        extra = Archive.parse_extra(info)
        assert_true(extra.has_key(0x5455))
        assert_equal(extra[0x5455], struct.pack('<Bl', 1, 978307200))
                
    def test_timestamps(self):
        foo = os.path.join('foobar', 'foo')
        os.utime(foo, (978307200,  978307200))
        
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version([foo])
        with rzip.TempUnrzip(apath) as zippath:
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                info = myzip.infolist()[0]
                assert_equal(info.date_time, (2001, 1, 1, 0, 0, 0))
                mtime = Archive.parse_extended_mtime(info)
                assert_equal(978307200, mtime)

    def test_external_attr(self):
        foo = os.path.join('foobar', 'foo')
        os.chmod(foo, 0644)
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version([foo])
        with rzip.TempUnrzip(apath) as zippath:
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                info = myzip.infolist()[0]
                assert_equal(info.external_attr, 0100644 << 16L)

from unittest import TestCase
from nose.tools import assert_equal
import sparchive.cli
from sparchive import mkstemppath
import os
from os import path
from sparchive import rzip
from zipfile import ZipFile
from tempfile import mkdtemp

class CliTest(TestCase):
    def setUp(self):
        self.olddir = os.getcwd()
        os.chdir(os.path.join('tests', 'fixtures'))

    def tearDown(self):
        os.chdir(self.olddir)

    @staticmethod
    def assert_ziprz_filenames(path, filenames):
        with rzip.TempUnrzip(path) as zippath:
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                assert_equal(set(filenames), set([ info.filename for info in myzip.infolist() ]))

    def test_cli(self):
        a = mkstemppath()
        foo = os.path.join('foobar', 'foo')
        bar = os.path.join('foobar', 'bar')
        sparchive.cli.main(["addversion", a, foo])
        sparchive.cli.main(["addversion", a, bar])
        assert(os.path.exists(a))
        with rzip.TempUnrzip(a) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                filenames = []
                for info in myzip.infolist():
                    filenames.append(info.filename)
                assert_equal(filenames, ["versions/0/foobar/foo", "versions/1/foobar/bar"])
        sparchive.cli.main(["list", a])
        
    def test_cli_file(self):
        archive = mkdtemp()
        foo = path.join('foobar', 'foo')
        sparchive.cli.main(['file', '-r', archive, foo])
        assert(path.exists(path.join(archive, '2001', '01', 'foo.zip.rz')))

    def test_cli_addversion(self):
        a = mkstemppath()
        os.chdir('foobar')
        sparchive.cli.main(['addversion', a, 'foo', 'bar'])
        CliTest.assert_ziprz_filenames(a, ['versions/0/foo', 'versions/0/bar'])

    def test_cli_extract(self):
        a = mkstemppath()
        foo = os.path.join('foobar', 'foo')
        bar = os.path.join('foobar', 'bar')
        sparchive.cli.main(["addversion", a, foo])
        sparchive.cli.main(["addversion", a, bar])
        xdir = mkdtemp()
        olddir = os.getcwd()
        os.chdir(os.path.join(xdir))
        sparchive.cli.main(["extract", a])
        os.chdir(olddir)
        xdir = os.path.join(xdir, os.path.basename(a))
        assert(os.path.exists(os.path.join(xdir, '0', 'foobar', 'foo')))
        assert_equal(open(foo, 'rb').read(), open(os.path.join(xdir, '0', 'foobar', 'foo'), 'rb').read())
        assert(os.path.exists(os.path.join(xdir,'1', 'foobar', 'bar')))
        assert_equal(open(bar, 'rb').read(), open(os.path.join(xdir, '1', 'foobar', 'bar'), 'rb').read())
#        shutil.rmtree(xdir)

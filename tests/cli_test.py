from unittest import TestCase
from nose.tools import assert_equal
import sparxive.cli
from sparxive import mkstemppath
import os
from os import path
from sparxive import rzip
from zipfile import ZipFile
from tempfile import mkdtemp

class CliTest(TestCase):
    def setUp(self):
        os.chdir(os.path.join('tests', 'fixtures'))

    def tearDown(self):
        os.chdir(os.path.join('..', '..'))

    def test_cli(self):
        a = mkstemppath()
        foo = os.path.join('foobar', 'foo')
        bar = os.path.join('foobar', 'bar')
        sparxive.cli.main(["addversion", a, foo])
        sparxive.cli.main(["addversion", a, bar])
        assert(os.path.exists(a))
        with rzip.TempUnrzip(a) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                filenames = []
                for info in myzip.infolist():
                    filenames.append(info.filename)
                assert_equal(filenames, ["0/foobar/foo", "1/foobar/bar"])
        sparxive.cli.main(["list", a])
        
    def test_cli_archive(self):
        archive = mkdtemp()
        foo = path.join('foobar', 'foo')
        sparxive.cli.main(['file', '-r', archive, foo])
        assert(path.exists(path.join(archive, '2013', '11', 'foo.zip.rz')))
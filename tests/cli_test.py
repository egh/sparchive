from unittest import TestCase
from nose.tools import assert_equal
import sparxive.cli
from sparxive import mkstemppath
import os
from sparxive import rzip
from zipfile import ZipFile

class CliTest(TestCase):
    def test_cli(self):
        a = mkstemppath()
        foo = os.path.join('tests', 'fixtures', 'foo')
        bar = os.path.join('tests', 'fixtures', 'bar')
        sparxive.cli.main(["add", a, foo])
        sparxive.cli.main(["add", a, bar])
        assert(os.path.exists(a))
        with rzip.TempUnrzip(a) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                filenames = []
                for info in myzip.infolist():
                    filenames.append(info.filename)
                assert_equal(filenames, ["0/tests/fixtures/foo", "1/tests/fixtures/bar"])

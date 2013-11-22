import os
from sparxive.archive import Archive
from unittest import TestCase
from nose.tools import assert_equal
from sparxive import mkstemppath

class TestArchive(TestCase):
    def test_add_file(self):
        p = os.path.join('tests', 'fixtures', 'foo')
        apath = mkstemppath()
        a = Archive(apath)
        a.add_version(p)
        a.add_version(p)
        print apath
        raise Exception        
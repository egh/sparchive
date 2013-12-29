import os
from sparchive import xz
from unittest import TestCase
from nose.tools import assert_equal
import hashlib
from sparchive import mkstemppath

class TestXz(TestCase):
    def test_compress_file(self):
        p = os.path.join('tests', 'fixtures', 'foobar', 'foo')
        prz = mkstemppath()
        assert(os.path.exists(p))
        assert(not(os.path.exists(prz)))
        xz.compress(p, prz)
        assert(os.path.exists(prz))
        assert_equal(hashlib.md5(open(prz, 'rb').read()).hexdigest(), "26fcf3231c59f1e991b9846b8e732452")
        os.unlink(prz)

    def test_uncompress_file(self):
        p = os.path.join('tests', 'fixtures', 'foobar', 'foo')
        prz = mkstemppath()
        pr2 = mkstemppath()
        xz.compress(p, prz)
        xz.uncompress(prz, pr2)
        
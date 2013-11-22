import os
from sparxiv import rzip
from unittest import TestCase
from nose.tools import assert_equal
import hashlib
from tempfile import mkstemp

class TestRzip(TestCase):
    def test_compress_file(self):
        p = os.path.join('tests', 'fixtures', 'foo')
        (_, prz) = mkstemp()
        os.unlink(prz)
        assert(os.path.exists(p))
        assert(not(os.path.exists(prz)))
        rzip.compress(p, prz)
        assert(os.path.exists(prz))
        assert_equal(hashlib.md5(open(prz).read()).hexdigest(), "dfa5ce71cda1c59f44eef332d4cb98cd")
        os.unlink(prz)

    def test_uncompress_file(self):
        p = os.path.join('tests', 'fixtures', 'foo')
        (_, prz) = mkstemp()
        os.unlink(prz)
        (_, pr2) = mkstemp()
        os.unlink(pr2)
        rzip.compress(p, prz)
        rzip.uncompress(prz, pr2)
        
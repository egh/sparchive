import os
import tempfile

def mkstemppath(suffix='', prefix='tmp', dir=None, text=False):
     (fd, path) = tempfile.mkstemp(suffix, prefix, dir, text)
     os.close(fd)
     os.unlink(path)
     return path

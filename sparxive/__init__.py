import os
import tempfile

def mkstemppath(suffix='', prefix='tmp', dir=None, text=False):
     (fd, path) = tempfile.mkstemp(suffix, prefix, dir, text)
     os.close(fd)
     os.unlink(path)
     return path

def find_file(dir, file):
     for root, dirs, files in os.walk(dir):
          if (file in files):
               return os.path.abspath(os.path.join(root, file))

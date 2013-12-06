import os
import tempfile

def mkstemppath(suffix='', prefix='tmp', dir=None, text=False):
     """Return the name of a temporary file that we can use."""
     f = tempfile.NamedTemporaryFile(delete=True)
     name = f.name
     f.close()
     return name


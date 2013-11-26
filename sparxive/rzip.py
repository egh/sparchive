import subprocess
from sparchive import mkstemppath
import os

def compress(uncompressed, compressed, level=6):
    args = ["rzip", uncompressed, "-k", "-%d"%(level), "-o", compressed]
    subprocess.check_call(args)
    
def uncompress(compressed, uncompressed):
    args = ["rzip", compressed, "-d", "-k", "-o", uncompressed]
    subprocess.check_call(args)

class TempUnrzip():
    def __init__(self, rzip_path):
        self.rzip_path = rzip_path

    def __enter__(self):
        self.uncomp_path = mkstemppath()
        if (os.path.exists(self.rzip_path)):
            uncompress(self.rzip_path, self.uncomp_path)
        return self.uncomp_path

    def __exit__(self, type, value, traceback):
        os.unlink(self.uncomp_path)


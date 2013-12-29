import subprocess
from sparchive import mkstemppath
import os

ext = "xz"

def compress(uncompressed, compressed, level=7):
    args = ["xz", uncompressed, "-z", "-k", "-%d"%(level), "-c"]
    subprocess.check_call(args, stdout=open(compressed, 'w'))
    
def uncompress(compressed, uncompressed):
    args = ["xz", compressed, "-d", "-c"]
    subprocess.check_call(args, stdout=open(uncompressed, 'w'))

class TempUncompress():
    def __init__(self, xz_path):
        self.xz_path = xz_path

    def __enter__(self):
        self.uncomp_path = mkstemppath()
        if (os.path.exists(self.xz_path)):
            uncompress(self.xz_path, self.uncomp_path)
        return self.uncomp_path

    def __exit__(self, type, value, traceback):
        os.unlink(self.uncomp_path)


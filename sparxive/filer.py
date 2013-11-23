import datetime
import os
import time

class Filer(object):
    def __init__(self, basedir):
        self.basedir = basedir
        
    def find_file(self, filename):
        for root, dirs, files in os.walk(self.basedir):
            if (filename in files):
                return os.path.abspath(os.path.join(root, filename))
        return None

    def get_mtime(self, path):
        def handle(path, times):
            if os.path.isdir(path):
                for name in os.listdir(path):
                    handle(os.path.join(path, name), times)
            elif os.path.isfile(path):
                # check if boring
                times.append(time.gmtime(os.path.getmtime(path)))
        times = []
        handle(path, times)
        times.sort()
        times.reverse()
        return times[0]

    def find_archive_path(self, pathname):
        """Find a path to a new or old archive which should be used to archive this path."""
        archivename = "%s.zip.rz"%(os.path.basename(pathname))
        old_archive = self.find_file(archivename)
        if old_archive is not None:
            return old_archive
        else:
            t = self.get_mtime(pathname)
            return os.path.join(self.basedir, "%d"(t.month), archivename)
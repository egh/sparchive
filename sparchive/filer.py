import datetime
import os
import time
from sparchive.archive import Archive

class Filer(object):
    def __init__(self, basedir, compress_module):
        self.basedir = basedir
        self.compress_module = compress_module

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

    def find_archive(self, pathname):
        """Find a new or old archive which should be used to archive this path."""
        archivename = "%s.zip.%s"%(os.path.basename(os.path.normpath(pathname)), self.compress_module.ext)
        old_archive = self.find_file(archivename)
        if old_archive is not None:
            return Archive(old_archive, self.compress_module)
        else:
            t = self.get_mtime(pathname)
            return Archive(os.path.join(self.basedir, "%04d"%(t.tm_year), "%02d"%(t.tm_mon), archivename), self.compress_module)
            
    def file(self, path):
        normpath = os.path.normpath(os.path.abspath(path))
        archive = self.find_archive(path)
        old_version = archive.has_version(path)
        if old_version is not None:
            return (False, old_version, archive)
        else:
            # there is a better way
            original_dir = os.getcwd()
            try:
                basename = os.path.basename(normpath)
                os.chdir(os.path.dirname(normpath))
                archive.add_version([basename])
                return (True, 0, archive)
            finally:
                os.chdir(original_dir)

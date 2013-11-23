from sparxive import rzip
from sparxive import mkstemppath
import re
import os
from zipfile import ZipFile
import time

def get_mtime(path):
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

class Archive(object):
    def __init__(self, archive_path):
        self.archive_path = archive_path

    def _get_info_version(self, info):
        """Returns the version number from a ZipInfo."""
        md = re.match(r"^([0-9]+)/", info.filename)
        if md is None:
            raise Exception()
        return int(md.group(1))
        
    def get_version_count(self, zippath):
        if not(os.path.exists(zippath)):
            return 0
        else:
            version_count = 0
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                for info in myzip.infolist():
                    this_version = self._get_info_version(info)
                    if (this_version+1) > version_count:
                        version_count = (this_version+1)
            return version_count

    def add_version(self, path):
        """Add a new version to this archive."""
        self.add_versions([path])

    def _add_path(self, path, version, myzip):
        if (os.path.isdir(path)):
            for name in os.listdir(path):
                self._add_path(os.path.join(path, name), version, myzip)
        elif (os.path.isfile(path)):
            myzip.write(path, "%d/%s"%(version, path))
        else:
            raise Exception()

    def add_versions(self, pathlist):
        """Add multiple versions to this archive."""
        for path in pathlist:
            if not(os.path.exists(path)):
                raise Exception()
        with rzip.TempUnrzip(self.archive_path) as zippath:
            new_version = self.get_version_count(zippath)
            with ZipFile(zippath, mode='a', allowZip64=True) as myzip:
                for path in pathlist:
                    self._add_path(path, new_version, myzip)
                    new_version = new_version + 1
            tmprzip = mkstemppath()
            rzip.compress(zippath, tmprzip)
        # perform sanity checks here
        os.rename(tmprzip, self.archive_path)

    def extract_version(self, number, dest):
        """Extract a version."""
        with rzip.TempUnrzip(self.archive_path) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                for info in myzip.infolist():
                    if (self._get_info_version(info) == number):
                        myzip.extract(info, dest)

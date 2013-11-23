from datetime import datetime
import os
import re
from zipfile import ZipFile

from sparxive import rzip
from sparxive import mkstemppath

class Archive(object):
    def __init__(self, archive_path):
        self.archive_path = archive_path

    def _split_path(self, info):
        """Splits a ZipInfo path into a versionnumber, path tuple."""
        md = re.match(r"^([0-9]+)/(.*)$", info.filename)
        if md is None:
            raise Exception()
        return (int(md.group(1)), md.group(2))
        
    def get_version_count(self, zippath):
        if not(os.path.exists(zippath)):
            return 0
        else:
            version_count = 0
            with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                for info in myzip.infolist():
                    this_version = self._split_path(info)[0]
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
                    if (self._split_path(info)[0] == number):
                        myzip.extract(info, dest)
    
    def list(self):
        with rzip.TempUnrzip(self.archive_path) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                retval = {}
                for info in myzip.infolist():
                    dt = datetime(*info.date_time)
                    (version, path) = self._split_path(info)
                    if not(retval.has_key(version)): retval[version] = []
                    retval[version].append((path, dt))
                return retval

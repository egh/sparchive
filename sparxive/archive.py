from sparxive import rzip
from sparxive import mkstemppath
import re
import os
from zipfile import ZipFile

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
            with ZipFile(zippath, 'r') as myzip:
                for info in myzip.infolist():
                    this_version = self._get_info_version(info)
                    if (this_version+1) > version_count:
                        version_count = (this_version+1)
            return version_count

    def add_version(self, path):
        """Add a new version to this archive."""
        with rzip.TempUnrzip(self.archive_path) as zippath:
            new_version = self.get_version_count(zippath)
            with ZipFile(zippath, 'a') as myzip:
                myzip.write(path, "%d/%s"%(new_version, path))
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
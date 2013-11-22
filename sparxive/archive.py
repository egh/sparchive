from sparxive import rzip
from sparxive import mkstemppath
import re
import os
from zipfile import ZipFile

class Archive(object):
    def __init__(self, archive_path):
        self.archive_path = archive_path

    def get_version_count(self, zippath):
        if not(os.path.exists(zippath)):
            return 0
        else:
            version_count = 0
            with ZipFile(zippath, 'r') as myzip:
                for info in myzip.infolist():
                    print info.filename
                    md = re.match(r"^([0-9]+)/", info.filename)
                    if md is None:
                        raise Exception()
                    this_version = int(md.group(1))
                    if (this_version+1) > version_count:
                        version_count = (this_version+1)
            return version_count

    def add_version(self, path):
        """Add a new version to this archive."""
        zippath = mkstemppath()
        if (os.path.exists(self.archive_path)):
            rzip.uncompress(self.archive_path, zippath)
        new_version = self.get_version_count(zippath)
        print new_version
        with ZipFile(zippath, 'a') as myzip:
            myzip.write(path, "%d/%s"%(new_version, path))
        tmprzip = mkstemppath()
        rzip.compress(zippath, tmprzip)
        # perform sanity checks here
        os.rename(tmprzip, self.archive_path)
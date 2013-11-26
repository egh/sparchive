from datetime import datetime
import os
import re
import binascii
from zipfile import ZipFile

from sparxive import rzip
from sparxive import mkstemppath

class Archive(object):
    def __init__(self, archive_path):
        self.archive_path = archive_path

    @staticmethod
    def _split_path(info):
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
                    this_version = Archive._split_path(info)[0]
                    if (this_version+1) > version_count:
                        version_count = (this_version+1)
            return version_count

    def _add_path(self, path, version, myzip):
        if (os.path.isdir(path)):
            for name in os.listdir(path):
                self._add_path(os.path.join(path, name), version, myzip)
        elif (os.path.isfile(path)):
            myzip.write(path, "%d/%s"%(version, path))
        else:
            raise Exception()

    def add_version(self, pathlist):
        """Add a version to this archive."""
        if not(os.path.isdir(os.path.dirname(self.archive_path))):
            os.makedirs(os.path.dirname(self.archive_path))
        for path in pathlist:
            if not(os.path.exists(path)):
                raise Exception()
        with rzip.TempUnrzip(self.archive_path) as zippath:
            new_version = self.get_version_count(zippath)
            with ZipFile(zippath, mode='a', allowZip64=True) as myzip:
                for path in pathlist:
                    self._add_path(path, new_version, myzip)
            tmprzip = mkstemppath()
            rzip.compress(zippath, tmprzip)
        # perform sanity checks here
        os.rename(tmprzip, self.archive_path)

    @staticmethod
    def _zip_versions(myzip):
        """Returns list of versions in the zip, where each version is a set
        of filename, crc tuples [[("a", crca1)], [("a", crca2), ("b", crcb2)]]".
        """
        retval = []
        for info in myzip.infolist():
            (version, p) = Archive._split_path(info)
            while len(retval) <= version:
                retval.append([])
            retval[version].append((p, info.CRC))
        return retval

    def has_version(self, path):
        """Return true if the archive already has a version that matchs path."""
        def mk_filename_set():
            if os.path.isfile(path):
                return set([path])
            else:
                filenames = []
                for root, dirs, files in os.walk(path):
                    filenames = filenames + [ os.path.join(root, filename) for filename in files ]
                return set(filenames)

        filename_set = mk_filename_set()
        filename_crc_set = None
        if (not(os.path.exists(self.archive_path))):
            return None
        else:
            with rzip.TempUnrzip(self.archive_path) as zippath:
                with ZipFile(zippath, mode='r', allowZip64=True) as myzip:
                    versions = Archive._zip_versions(myzip)
                    for (versionno, version) in enumerate(versions):
                        # first check the files without CRC
                        version_files = [ p[0] for p in version ]
                        if set(version_files) == filename_set:
                            if filename_crc_set is None:
                                filename_crc_set = set([ (f, Archive._crc32(f)) for f in filename_set ])
                            if set(version) == filename_crc_set:
                                return versionno
            return None

    @staticmethod
    def _crc32(filename):
        with open(filename, 'rb') as fd:
            buff = fd.read(16384)
            sofar = (binascii.crc32(buff) & 0xffffffff)
            buff = fd.read(16384)
            while (buff != ""):
                sofar = (binascii.crc32(buff, sofar) & 0xffffffff)
                buff = fd.read(16384)
            return sofar 

    def extract(self, dest, number=None):
        """Extract a version."""
        with rzip.TempUnrzip(self.archive_path) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                for info in myzip.infolist():
                    if number is None:
                        myzip.extract(info, dest)
                    elif (Archive._split_path(info)[0] == number):
                        myzip.extract(info, dest)
    
    def list(self):
        with rzip.TempUnrzip(self.archive_path) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                retval = {}
                for info in myzip.infolist():
                    dt = datetime(*info.date_time)
                    (version, path) = Archive._split_path(info)
                    if not(retval.has_key(version)): retval[version] = []
                    retval[version].append((path, dt))
                return retval

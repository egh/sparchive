import shutil
import struct
from datetime import datetime
import os
import re
import binascii
from zipfile import ZipFile, ZipInfo
import time

from sparchive import rzip
from sparchive import mkstemppath

class Archive(object):
    def __init__(self, archive_path):
        self.archive_path = archive_path

    @staticmethod
    def get_mtime_as_utcdatetime(path):
        return datetime.utcfromtimestamp(os.path.getmtime(path))

    @staticmethod
    def unixtime_to_utcziptime(utime):
        epoch = 315532800 # calendar.timegm((1980, 1, 1, 0, 0, 0, 1, 1, 0))
        if utime < epoch: utime = epoch
        return time.gmtime(utime)[:6]
    
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

    ZIP_EXT_ATTR_FILE = 0100000L
    ZIP_EXT_ATTR_DIR  = 0040000L
    ZIP_EXT_ATTR_LINK = 0120000L

    def _add_path(self, path, version, myzip):
        mtime = os.path.getmtime(path)
        info = ZipInfo("%d/%s"%(version, path), Archive.unixtime_to_utcziptime(mtime))
        info.create_system = 3
        info.extra += struct.pack('<HHBl', 0x5455, 5, 1, mtime)
        # http://unix.stackexchange.com/questions/14705/the-zip-formats-external-file-attribute
        # make mode without file type, which may be system-specific
        clean_mode = os.stat(path).st_mode & 0007777
        if (os.path.islink(path)):
            # set zip file type to link
            info.external_attr = (Archive.ZIP_EXT_ATTR_LINK | clean_mode) << 16L
            myzip.writestr(info, os.readlink(path))
        elif (os.path.isdir(path)):
            # set zip file type to dir 
            info.external_attr = (Archive.ZIP_EXT_ATTR_DIR | clean_mode) << 16L
            # dos directory flag
            info.external_attr |= 0x10
            # it seems we should have a trailing slash for dirs
            if not(info.filename.endswith('/')): info.filename = "%s/"%(info.filename)
            myzip.writestr(info, '')
            for name in os.listdir(path):
                self._add_path(os.path.join(path, name), version, myzip)
        elif (os.path.isfile(path)):
            info.external_attr = (Archive.ZIP_EXT_ATTR_FILE | clean_mode) << 16L
            myzip.writestr(info, open(path).read())
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
    def parse_extra(info):
        pos = 0
	extra = {}
        while (pos < len(info.extra)):
            header, size = struct.unpack_from('<HH', info.extra, pos)
            pos += 4
            extra[header] = info.extra[pos:(pos + size)]
            pos += size
        return extra

    @staticmethod
    def parse_extended_mtime(info):
        extra = Archive.parse_extra(info)
        if extra.has_key(0x5455):
            flags, mtime = struct.unpack("<Bl", extra[0x5455])
            return mtime
        else:
            return None

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
                filenames = [path + "/"]
                for root, dirs, files in os.walk(path):
                    filenames += [ os.path.join(root, filename) for filename in files ]
                    filenames += [ os.path.join(root, d) + "/" for d in dirs ]
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
        if os.path.islink(filename):
            return binascii.crc32(os.readlink(filename)) & 0xffffffff
        elif os.path.isdir(filename):
            return 0
        elif os.path.isfile(filename):
            with open(filename, 'rb') as fd:
                buff = fd.read(16384)
                sofar = (binascii.crc32(buff) & 0xffffffff)
                buff = fd.read(16384)
                while (buff != ""):
                    sofar = (binascii.crc32(buff, sofar) & 0xffffffff)
                    buff = fd.read(16384)
                return sofar 
        else:
            raise Exception()

    @staticmethod
    def islink_entry(info):
        return ((info.external_attr >> 16L) & Archive.ZIP_EXT_ATTR_LINK) == Archive.ZIP_EXT_ATTR_LINK

    @staticmethod
    def isdir_entry(info):
        return ((info.external_attr >> 16L) & Archive.ZIP_EXT_ATTR_DIR) == Archive.ZIP_EXT_ATTR_DIR

    def _extract_entry(self, myzip, info, destdir):
        dest = os.path.normpath(os.path.join(destdir, info.filename))

        parentdirs = os.path.dirname(dest)
        if parentdirs and not os.path.exists(parentdirs):
            os.makedirs(parentdirs)

        if (os.path.exists(dest)):
            raise Exception()

        if Archive.islink_entry(info):
            i = myzip.open(info)
            target = i.read()
            i.close()
            os.symlink(target, dest)
        else:
            if (info.filename[-1] == '/' or Archive.isdir_entry(info)) and not(os.path.isdir(dest)):
                os.mkdir(dest)
            else:
                i = myzip.open(info)
                o = file(dest, "wb")
                shutil.copyfileobj(i, o)
                i.close()
                o.close()

            # parse extended datetime
            mtime = Archive.parse_extended_mtime(info)
            if mtime is not None:
                os.utime(dest, (mtime, mtime))
            # extract permissions
            os.chmod(dest, info.external_attr >> 16L & 0007777)

    def extract(self, dest, number=None):
        """Extract a version."""
        with rzip.TempUnrzip(self.archive_path) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                for info in myzip.infolist():
                    # call _split_path for every entry to ensure they
                    # are name properly
                    versionno, name = Archive._split_path(info)
                    if number is None or (number == versionno):
                        self._extract_entry(myzip, info, dest)
    
    def list(self):
        with rzip.TempUnrzip(self.archive_path) as zippath:
            with ZipFile(zippath, 'r') as myzip:
                retval = {}
                for info in myzip.infolist():
                    (version, path) = Archive._split_path(info)
                    if not(retval.has_key(version)): retval[version] = []
                    retval[version].append((path, info))
                return retval

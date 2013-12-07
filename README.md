sparchive
=========

sparchive is a simple, personal digital archival utility. It stores
your old files in a compact, versioned format that does not depend on
filesystem metadata (modification time, file name); this data is
stored within the archive file itself.

sparchive includes a "filer" program, which "files" your files and
directories into an archive directory.

sparchive is in *active development*. The file format may change without
notice!

Use cases
---------

You are writing a document, `foo.odt`. You have reached a point where
you want to archive a copy of this document. Type:

    sparchive file foo.odt

This will archive a copy foo.odt in a file called foo.odt.zip.rz,
stored in your archive dir (by default, `~/a`) in a simple year/month
directory tree, e.g. `2013/11/foo.odt.zip.rz`.

Now, after some time, you have made some changes to `foo.odt`, you can
archive a new version:

    sparchive file foo.odt

This will add a new version to your `2013/11/foo.odt.zip.rz` file.

You can do the same thing with directories:

    sparchive file dir/

Which will add a `2013/11/dir.zip.rz` file to your achive.

Because of sparchive's file format, similar data will be losslessly
compressed. So if, like me, you often end up with multiple directories
with similar files, you can safely file them away and sparchive will
store them in an efficent manner.

Extracting
----------

When extacting an archive (using `sparchive extract`), sparchive will
create a directory in the current working directory with the same name
as the archive, e.g. for an archive named `foo.zip.rz` it will create
a directory named `foo`. 

Installation
------------

sparchive is developed on Linux and should work on any Unix (including
Mac OS X). It is written in Python 2.7 and requires an rzip binary.
Running:

    python setup.py install

possibly as sudo, should be sufficient to install.

File format
-----------

sparchive first stores data in standard ZIP files. sparchive *stores*
data in the ZIP; it does not *compress* (deflate) the data.
Compression is handled by rzip. rzip is capable of exploiting
similarities between files (and therefore between versions), and so
should achieve very good compression ratios for similar versions. As a
quick example, I created a sparchive file containing 10 versions of a
SQL dump (which did not change much from day to day), each version of
which takes up 12MB (uncompressed) or about 4.3MB gzipped. The
sparchive file was 2.2 MB.

### zip directory structure ###

sparchive stores each version in a directory with the version number
(starting from 1) as the name of the directory. These directories are
stored under a `versions` directory at the toplevel of the zip file.

### Some more details about the ZIP ###

sparchive files use the extended timestamp extra field to store last
modified time, and the external attributes to store permissions (but
not owners). Timestamps and permissions should be preserved for files
and directories.

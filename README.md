sparchive
=========

sparchive is a simple, personal digital archival utility. It stores
your old files or directories in a compact, versioned format that does
not depend on filesystem metadata (modification time, file name); this
data is stored within the archive file itself. sparchive utilizes
similarities between files and versions to achieve a high level of
compression.

sparchive includes a "filer" program, which "files" your files and
directories into an archival directory, storing your archives
according the to the last modified dates.

sparchive is in *active development*. The file format may change
without notice!

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

Because of sparchive's file format, similar data will be compressed.
So if, like me, you often end up with multiple directories with
similar files, you can safely file them away and sparchive will store
them in an efficent manner.

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

Concepts
--------

By storing data in a ZIP file, sparchive leverages the ZIP file format
to manage file metadata and to bundle a group of files into a single
file. The ZIP file format is a well known, widely implemented
standard.

By not compressing the data within the ZIP file, but instead
compressing the entire ZIP file using another compression utility,
sparchive is able to leverage similarities *across* files while
compressing. This means that if you are storing multiple versions,
sparchive can exhibit high levels of compression by utilizing
similarities in files between versions.

By using the standard ZIP format and a compression wrapper, sparchive
archive files are extractable on any device that supports zip and the
compression wrapper, *without* requiring the sparchive program itself.

sparchive leaves the format of your archival directories up to you.
You can easily store any metadata format within your versioned
directories.

Tests
-----
-   xz, 1000 versions, 10000 random ascii characters (base) + 100 random ascii characters
    real	47m44.294s
    user	43m38.820s
    sys	3m12.168s
    result file: 107560 bytes

-   rzip, 1000 versions, 10000 random ascii characters (base) + 100 random ascii characters
    real	7m27.194s
    user	5m2.294s
    sys	2m3.506s
    result file: 108740 bytes

### 10gb benchmark
http://mattmahoney.net/dc/10gb.html
-   rzip, 10gb benchmark
2410.27user 132.12system 50:43.73elapsed 83%CPU (0avgtext+0avgdata 1001128maxresident)k
38220368inputs+27216728outputs (2890major+17593381minor)pagefaults 0swaps

-   zpaq, 10gb benchmark
900.17user 57.16system 18:25.97elapsed 86%CPU (0avgtext+0avgdata 247956maxresident)k
19762561inputs+7487344outputs (6major+8627019minor)pagefaults 0swaps

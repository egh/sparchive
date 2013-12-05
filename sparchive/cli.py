from datetime import datetime
import argparse
import sys
from sparchive.archive import Archive
from sparchive.filer import Filer
from os import path

def main(rawargs=None):
     if rawargs is None: rawargs = sys.argv[1:]
     parser = argparse.ArgumentParser(description='sparkive - simple python archiver')
     subparsers = parser.add_subparsers()

     filer = subparsers.add_parser('file')
     filer.add_argument('-r', '--root', help='root of archive', default=path.join(path.expanduser("~"), "a"))
     filer.add_argument('version_path', nargs="+", help='paths to version to add', default=None)
     filer.set_defaults(command='file')

     addversion = subparsers.add_parser("addversion")
     addversion.add_argument('archive', help='archive file')
     addversion.add_argument('version_path', nargs="+", help='path to version to add', default=None)
     addversion.set_defaults(command='addversion')

     ls = subparsers.add_parser("list")
     ls.add_argument('archive', help='archive file')
     ls.set_defaults(command='list')

     extract = subparsers.add_parser("extract")
     extract.add_argument('archive', help='archive file to extract from')
     extract.add_argument('version', nargs="?", help='version number to extract', default=None)
     extract.add_argument('path', nargs="*", help='path to extract')
     extract.set_defaults(command='extract')

     args = parser.parse_args(rawargs)
     if args.command == "addversion":
          a = Archive(args.archive)
          a.add_version(args.version_path)
     elif args.command == "file":
          filer = Filer(path.abspath(args.root))
          for p in args.version_path:
               result = filer.file(p)
               if result[0]:
                    sys.stdout.write("%s archived in %s\n"%(p, result[2].archive_path))
               else:
                    sys.stdout.write("%s is already archived in version %d of %s\n"%(p, result[1], result[2].archive_path))
     elif args.command == "list":
          d = Archive(args.archive).list()
          for n in sorted(d.keys()):
               print "version %d:"%n
               for (p, info) in d[n]:
                    dt = datetime(*info.date_time)
                    mtime = Archive.parse_extended_mtime(info)
                    mdatetime = datetime.fromtimestamp(mtime)
                    print "  %s  (%d, %s)"%(p, info.file_size, mdatetime.strftime("%Y-%m-%d %H:%M:%S"))
     elif args.command == "extract":
          a = Archive(args.archive)
          a.extract(".", args.version)

if __name__ == "__main__":
    main()

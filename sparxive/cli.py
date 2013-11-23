import argparse
import sys
from sparxive.archive import Archive
from sparxive.filer import Filer
from os import path

def main(rawargs=None):
     if rawargs is None: rawargs = sys.argv[1:]
     parser = argparse.ArgumentParser(description='sparkive - simple python archiver')
     subparsers = parser.add_subparsers()

     archive = subparsers.add_parser('archive')
     archive.add_argument('-r', '--root', help='root of archive', default='/tmp')
     archive.add_argument('version_path', nargs="+", help='paths to version to add', default=None)
     archive.set_defaults(command='archive')

     addversion = subparsers.add_parser("addversion")
     addversion.add_argument('archive', help='archive file')
     addversion.add_argument('version_path', help='path to version to add', default=None)
     addversion.set_defaults(command='addversion')

     ls = subparsers.add_parser("list")
     ls.add_argument('archive', help='archive file')
     ls.set_defaults(command='list')

     args = parser.parse_args(rawargs)
     if args.command == "addversion":
          a = Archive(args.archive)
          a.add_version(args.version_path)
     elif args.command == "archive":
          filer = Filer(path.abspath(args.root))
          for p in args.version_path:
               archive = filer.find_archive(p)
               old_version = archive.has_version(p)
               if old_version is not None:
                    sys.stderr.write("That is already archived in version %d of %s.\n"%(old_version, archive.archive_path))
                    sys.exit(1)
               else:
                    archive.add_version(p)
     elif args.command == "list":
          d = Archive(args.archive).list()
          for n in sorted(d.keys()):
               print "version %d:"%n
               for (p, dt) in d[n]:
                    print "  %s  (%s)"%(p, dt.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()

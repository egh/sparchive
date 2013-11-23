import argparse
import sys
from sparxive.archive import Archive

def main(rawargs=None):
     if rawargs is None: rawargs = sys.argv[1:]
     parser = argparse.ArgumentParser(description='sparkive - simple python archiver')
     parser.add_argument('COMMAND', help='command to run', choices=['add', 'extract', 'list', 'search'])
     parser.add_argument('archive', help='archive file')
     parser.add_argument('version_path', nargs="?", help='path to version to add', default=None)
     args = parser.parse_args(rawargs)
     if (args.COMMAND == "add"):
          if (args.version_path is None):
               sys.stderr("You must provide a path to a version to add!")
          else:
               a = Archive(args.archive)
               a.add_version(args.version_path)
     elif args.COMMAND == "extract":
          pass
     elif args.COMMAND == "list":
          d = Archive(args.archive).list()
          for n in sorted(d.keys()):
               print "version %d:"%n
               for (p, dt) in d[n]:
                    print "  %s  (%s)"%(p, dt.strftime("%Y-%m-%d %H:%M:%S"))
     elif args.COMMAND == "search":
          pass

if __name__ == "__main__":
    main()

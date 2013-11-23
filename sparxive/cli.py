import argparse
import sys
from sparxive.archive import Archive

def main(rawargs=None):
     if rawargs is None: rawargs = sys.argv[1:]
     parser = argparse.ArgumentParser(description='sparkive - simple python archiver')
     parser.add_argument('COMMAND', help='command to run', choices=['add', 'extract', 'list', 'search'])
     parser.add_argument('archive', nargs=1, help='archive file')
     parser.add_argument('version_path', nargs=1, help='path to version to add')
     args = parser.parse_args(rawargs)
     if (args.COMMAND == "add"):
         a = Archive(args.archive[0])
         a.add_version(args.version_path[0])
     elif args.COMMAND == "extract":
          pass
     elif args.COMMAND == "list":
          d = Archive(args.archive[0]).list()
          for n in sorted(d.keys()):
               print "version %d:"%n
               for (p, dt) in d[n]:
                    print "  %s  (%s)"%(p, dt.strftime("%Y-%m-%d %H:%M:%S"))
     elif args.COMMAND == "search":
          pass

if __name__ == "__main__":
    main()

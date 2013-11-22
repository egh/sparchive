import argparse
import sys
import os
import tempfile

def mkstemppath(suffix='', prefix='tmp', dir=None, text=False):
     (fd, path) = tempfile.mkstemp(suffix, prefix, dir, text)
     os.close(fd)
     os.unlink(path)
     return path

def main(rawargs=None):
     if rawargs is None: rawargs = sys.argv[1:]
     parser = argparse.ArgumentParser(description='sparkive - simple python archiver')
     parser.add_argument('COMMAND', nargs=1, help='command to run', choices=['add', 'extact', 'search'])
     args = parser.parse_args(rawargs)
     if args.COMMAND == "add":
          pass
     elif args.COMMAND == "extract":
          pass
     elif args.COMMAND == "search":
          pass

if __name__ == "__main__":
    main()

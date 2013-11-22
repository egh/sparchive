import argparse
import sys

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

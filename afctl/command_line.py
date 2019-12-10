__author__ = 'Aaditya Sharma'

from afctl.parsers import Parser
import sys

def main():
    parser = Parser.setup_parser()
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.error('No arguments provided.')

    args.func(args)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(e)

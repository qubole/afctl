from afctl.parsers import Parser
import sys

def main():
    parser = Parser.setup_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())

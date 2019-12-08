from afctl.parsers import setup_parser
import sys

def main():
    parser = setup_parser()
    parser.parse_known_args()

if __name__ == '__main__':
    sys.exit(main())

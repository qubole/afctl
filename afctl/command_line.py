__author__ = 'Aaditya Sharma'

from afctl.parsers import Parser
from afctl.exceptions import AfctlParserException
import logging
import sys

def main():
    try:
        parser = Parser.setup_parser()
        args = parser.parse_args()

        if not any(vars(args).values()):
            parser.error('No arguments provided.')

        args.func(args)

    except AfctlParserException as e:
        logging.error(e)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        logging.error(e)
        print(e)

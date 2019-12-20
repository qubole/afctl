import argparse
import logging
import yaml
import sys
import os
from afctl import __version__
from afctl.utils import Utility
from afctl.exceptions import AfctlParserException

class Parser():

    @classmethod
    def setup_parser(cls):

        cls.parser = argparse.ArgumentParser(description="A CLI tool to make deployment of airflow projects faster")
        cls.parser.add_argument("-v", "--version", action='version', version=__version__)
        all_subparsers = cls.get_subparsers()
        subparsers = cls.parser.add_subparsers()
        for sp in all_subparsers:
            sub_parser = subparsers.add_parser(sp['parser'], help=sp['help'])
            sub_parser.set_defaults(func=sp['func'])
            for arguments in sp['args']:
                arg = dict(a.split('=') for a in arguments[1:])
                sub_parser.add_argument(arguments[0], **arg)

        return cls.parser


    @classmethod
    def init(cls, args):
        try:
            pwd = os.getcwd()
            main_dir = [os.path.join(pwd, args.name)]
            sub_files = ['__init__.py', 'afctl_project_meta.yml']

            if os.path.exists(main_dir[0]):
                logging.error("Project already exists. Please delete entry under afctl_congfis after removing the project from current directory.")
                cls.parser.error("Project name already exists.")

            print("Initializing new project...")
            logging.info("Project initialization started.")

            # Create parent dir
            os.mkdir(main_dir[0])

            #create file
            Utility.create_files(main_dir, sub_files)

            print("New project initialized successfully.")
            logging.info("Project created.")

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def list(cls, args):
        try:
            print("Available {} :".format(args.type))
            logging.info("Available {} :".format(args.type))
            print('\n'.join(map(str, cls.read_meta()[args.type])))
            logging.info('\n'.join(map(str, cls.read_meta()[args.type])))

        except Exception as e:
            raise AfctlParserException(e)


########################################################################################################################
    # ALL THE METHODS DOWN HERE RETURN VALUES.
    # PLEASE FOLLOW THE CONVENTION TO KEEP THE CODE MAINTAINABLE
########################################################################################################################


    @classmethod
    def read_meta(cls):
        try:
            with open("{}/{}".format(os.path.dirname(os.path.abspath(__file__)), 'meta.yml')) as file:
                data = yaml.full_load(file)
            operators = "" if data['operators'] is None else data['operators'].split(' ')
            hooks = "" if data['hooks'] is None else data['hooks'].split(' ')
            sensors = "" if data['sensors'] is None else data['sensors'].split(' ')
            plugins = "" if data['connectors'] is None else data['connectors'].split(' ')

            return {'operators':operators, 'hooks':hooks, 'sensors':sensors, 'plugins':plugins}

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def get_subparsers(cls):
        subparsers = (
            {
                'func': cls.init,
                'parser': 'init',
                'help': 'Create a new Airflow project.',
                'args': [
                    ['name', "help=Name of your airflow project"]
                ]
            },

            {
                'func': cls.list,
                'parser': 'list',
                'help': 'Get list of operators, sensors, connectors and  hooks.',
                'args': [
                    ['type', "choices=['operators', 'sensors', 'connectors', 'hooks']"]
                ]
            }
        )
        return subparsers
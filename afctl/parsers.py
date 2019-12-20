import argparse
import logging
import yaml
import sys
import os
from afctl import __version__
from afctl.utils import Utility

class Parser():



    @classmethod
    def setup_parser(cls):
        cls.read_meta()
        cls.parser = argparse.ArgumentParser(description="A CLI tool to make deployment of airflow projects faster")
        cls.parser.add_argument("-v", "--version", action='version', version=__version__)
        new_parser = cls.parser.add_subparsers()
        sub_parser = new_parser.add_parser("init", help="Create a boilerplate code for your airflow project")
        sub_parser.set_defaults(func=cls.create_project)
        sub_parser.add_argument("-n", "--name", help="Name of your airflow project", required=True)
        sub_parser.add_argument("-p", "--plugin", help="Add plugin to your project", choices=cls.plugins, required=True)
        sub_parser = new_parser.add_parser("list", help="Get list of operators, sensors, connectors and  hooks.")
        sub_parser.set_defaults(func=cls.list)
        sub_parser.add_argument("type", choices=cls.choices)
        return cls.parser

    @classmethod
    def create_project(cls, args):
        try:
            pwd = os.getcwd()
            main_dir = [os.path.join(pwd, args.name)]
            sub_files = ['__init__.py', 'meta.yml']

            if os.path.exists(main_dir[0]):
                cls.parser.error("Project already exists.")

            print("Initializing new project...")

            # Create parent dir
            os.mkdir(main_dir[0])

            #create file
            Utility.create_files(main_dir, sub_files)

            print("New project initialized successfully.")

        except Exception as e:
            logging.exception("Error in  creating project.")

    @classmethod
    def list(cls, args):
        print("Available {} :".format(args.type))
        vals = eval("cls.{}".format(args.type))
        print('\n'.join(map(str, vals)))

    @classmethod
    def read_meta(cls):
        try:
            with open("{}/{}".format(os.path.dirname(os.path.abspath(__file__)), 'meta.yml')) as file:
                cls.data = yaml.full_load(file)

            cls.choices = [k for k in cls.data]
            cls.operators = "" if cls.data['operators'] is None else cls.data['operators'].split(' ')
            cls.hooks = "" if cls.data['hooks'] is None else cls.data['hooks'].split(' ')
            cls.sensors = "" if cls.data['sensors'] is None else cls.data['sensors'].split(' ')
            cls.plugins = "" if cls.data['connectors'] is None else cls.data['plugins'].split(' ')
        except Exception as e:
            logging.exception("Error in reading meta.yml")
            sys.exit(3)

import argparse
import yaml
import sys
import os
from afctl import __version__
from afctl.utils import Utility

class Parser():

    @classmethod
    def setup_parser(cls):
        cls._read_meta()
        cls.parser = argparse.ArgumentParser(description="A CLI tool to make deployment of airflow projects faster")
        cls.parser.add_argument("-v", "--version", action='version', version=__version__)
        new_parser = cls.parser.add_subparsers()
        sub_parser = new_parser.add_parser("init", help="Create a boilerplate code for your airflow project")
        sub_parser.set_defaults(func=cls._create_project)
        sub_parser.add_argument("-n", "--name", help="Name of your airflow project", required=True)
        sub_parser.add_argument("-p", "--plugin", help="Add plugin to your project", choices=cls.plugins, required=True)
        sub_parser = new_parser.add_parser("list", help="Get list of operators, sensors, plugins, hooks.")
        sub_parser.set_defaults(func=cls._list)
        sub_parser.add_argument("type", choices=cls.choices)
        return cls.parser

    @classmethod
    def _create_project(cls, args):
        pwd = os.getcwd()
        main_dir = [os.path.join(pwd, args.name)]
        sub_files = ['requirements.txt', 'setup.py', '.gitignore']
        sub_dir = [args.name]
        sub_dir_files = ['__init__.py', 'command_line.py', 'parser.py', 'meta.yml']

        if os.path.exists(main_dir[0]):
            cls.parser.error("Project already exists.")

        print("Initializing new project...")

        # Create parent dir
        os.mkdir(main_dir[0])

        # Create sub files
        Utility.create_files(main_dir, sub_files)

        # Create sub dir
        Utility.create_dirs(main_dir, sub_dir)

        # Create sub dir files
        package_dir = ["{}/{}".format(main_dir[0], args.name)]
        Utility.create_files(package_dir, sub_dir_files)

        print("New project initialized successfully.")

    @classmethod
    def _list(cls, args):
        print("Available {} :".format(args.type))
        vals = eval("cls.{}".format(args.type))
        print('\n'.join(map(str, vals)))

    @classmethod
    def _read_meta(cls):
        try:
            with open("{}/{}".format(os.path.dirname(os.path.abspath(__file__)), 'meta.yml')) as file:
                cls.data = yaml.full_load(file)

            cls.choices = [k for k in cls.data]
            cls.operators = cls.data['operators'].split(' ')
            cls.hooks = cls.data['hooks'].split(' ')
            cls.sensors = cls.data['sensors'].split(' ')
            cls.plugins = cls.data['plugins'].split(' ')
        except:
            sys.exit(3)

import argparse
import logging
import yaml
import sys
import os
from afctl import __version__
from afctl.utils import Utility
from afctl.exceptions import AfctlParserException
import subprocess

class Parser():

    @classmethod
    def setup_parser(cls):
        try:
            cls.parser = argparse.ArgumentParser(description="A CLI tool to make deployment of airflow projects faster")
            cls.parser.add_argument("-v", "--version", action='version', version=__version__)
            all_subparsers = cls.get_subparsers()
            subparsers = cls.parser.add_subparsers()
            for sp in all_subparsers:
                sub_parser = subparsers.add_parser(sp['parser'], help=sp['help'])
                sub_parser.set_defaults(func=sp['func'])
                for arguments in sp['args']:
                    arg = {}
                    for ag in arguments[1:]:
                        for k,v in ag.items():
                            arg[k] = v
                    sub_parser.add_argument(arguments[0], **arg)
            return cls.parser

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def init(cls, args):
        try:
            pwd = os.getcwd()
            main_dir = [os.path.join(pwd, args.name)]
            config_dir = '{}/afctl_config'.format(os.path.expanduser("~"))
            config_file = "{}/{}.yml".format(config_dir, args.name)
            sub_files = ['__init__.py', 'afctl_project_meta.yml']

            if not os.path.exists(config_dir):
                os.mkdir(config_dir)

            if os.path.exists(main_dir[0]) or os.path.exists(config_file):
                logging.error("Project already exists. Please delete entry under afctl_congfis after removing the project from the current directory.")
                cls.parser.error("Project already exists.")

            print("Initializing new project...")
            logging.info("Project initialization started.")

            # Create parent dir
            os.mkdir(main_dir[0])

            #create file
            files = Utility.create_files(main_dir, sub_files)
            os.system("echo 'project: {}' >> {}".format(args.name, files[sub_files[1]]))

            #create config file
            os.system("cat {}/plugins/connectors/connection_config.yml >> {}".format(os.path.dirname(os.path.abspath(__file__)), config_file))

            print("New project initialized successfully.")
            logging.info("Project created.")

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def list(cls, args):
        try:
            print("Available {} :".format(args.type))
            logging.info("Printing list on the console.")
            print('\n'.join(map(str, cls.read_meta()[args.type])))

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def add_config(cls, args):
        try:
            file = '{}/afctl_config/{}.yml'.format(os.path.expanduser("~"), args.project)
            if not os.path.exists(file):
                cls.parser.error("Project configuration file does not exists in afctl_config")
                logging.error("Project does not exists")

            cmd = os.environ.get('EDITOR', 'vi') + ' ' + file
            subprocess.call(cmd, shell=True)
            logging.info("Configuration added.")
            print("Configuration added.")

        except Exception as e:
            raise AfctlParserException(e)

########################################################################################################################

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
                    ['name', {'help':'Name of your airflow project'}]
                ]
            },

            {
                'func': cls.list,
                'parser': 'list',
                'help': 'Get list of operators, sensors, connectors and  hooks.',
                'args': [
                    ['type', {'choices':['operators', 'sensors', 'connectors', 'hooks'], 'help':'Choose from the options.'}]
                ]
            },

            {
                'func': cls.add_config,
                'parser': 'add_config',
                'help': 'Add configurations for your connection.',
                'args': [
                    ['project', {'help':'Name of the project for which you want to add connection configurations.'}]
                ]
            }
        )
        return subparsers
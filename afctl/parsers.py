import argparse
import logging
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
            main_dir = pwd if args.name == '.' else os.path.join(pwd, args.name.lstrip('/').rstrip('/'))
            project_name = os.path.basename(main_dir)
            config_dir = Utility.CONSTS['config_dir']
            config_file = "{}/{}.yml".format(config_dir, project_name)
            sub_files = ['__init__.py', 'afctl_project_meta.yml']

            if not os.path.exists(config_dir):
                os.mkdir(config_dir)

            if os.path.exists(main_dir) and os.path.exists(config_file):
                logging.error("Project already exists. Please delete entry under afctl_congfis after removing the project from the current directory.")
                cls.parser.error("Project already exists.")

            print("Initializing new project...")
            logging.info("Project initialization started.")

            # STEP - 1: Create parent dir
            if args.name != '.':
                os.mkdir(main_dir)

            # STEP - 2: create files
            files = Utility.create_files([main_dir], sub_files)
            os.system("echo 'project: {}' >> {}".format(project_name, files[sub_files[1]]))

            #STEP - 3: create config file
            os.system("cat {}/plugins/deployments/deployment_config.yml >> {}".format(os.path.dirname(os.path.abspath(__file__)), config_file))

            #STEP - 4: Add git origin.
            origin = subprocess.run(['git', '--git-dir={}/.git'.format(main_dir), 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE)
            origin = origin.stdout.decode('utf-8')[:-1]
            if origin == '':
                print("Git origin is not set for this repository. Run 'afctl config global -o {origin}'")
            else:
                Utility.update_config(project_name, {'global':{'origin':origin}})
                print("Setting origin as : {}".format(origin))
                logging.info("Origin set as : {}".format(origin))

            print("New project initialized successfully.")
            logging.info("Project created.")

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def list(cls, args):
        try:
            print("Available {} :".format(args.type))
            logging.info("Printing list on the console.")
            print('\n'.join(map(str, Utility.read_meta()[args.type])))

        except Exception as e:
            raise AfctlParserException(e)

########################################################################################################################

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
                    ['type', {'choices':['operators', 'sensors', 'deployment', 'hooks'], 'help':'Choose from the options.'}]
                ]
            }
        )
        return subparsers
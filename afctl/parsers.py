__author__ = 'Aaditya Sharma'

import argparse
import logging
import os
from afctl import __version__
from afctl.utils import Utility
from afctl.exceptions import AfctlParserException
import subprocess
from afctl.plugins.deployments.deployment_config import DeploymentConfig


class Parser():

    @classmethod
    def setup_parser(cls):
        try:
            cls.parser = argparse.ArgumentParser(description="A CLI tool to make deployment of airflow projects faster")
            cls.parser.add_argument("-v", "--version", action='version', version=__version__)
            all_subparsers = cls.get_subparsers()
            subparsers = cls.parser.add_subparsers()
            for sp in all_subparsers:
                sub_parser = subparsers.add_parser(sp['parser'], usage=sp['help'])
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
            config_file = Utility.project_config(project_name)
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
            os.system("cat {}/plugins/deployments/deployment_config.yml > {}".format(os.path.dirname(os.path.abspath(__file__)), config_file))

            #STEP - 4: Add git origin.
            origin = subprocess.run(['git', '--git-dir={}'.format(os.path.join(main_dir, '.git')), 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE)
            origin = origin.stdout.decode('utf-8')[:-1]
            if origin == '':
                print("Git origin is not set for this repository. Run 'afctl config global -o <origin>'")
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

    @classmethod
    def config(cls, args):
        try:
            logging.info("Config method called")
            config_file = cls.validate_project(args.p)

            if config_file is None:
                cls.parser.error("Invalid project.")
                logging.error("Invalid project.")

            # Setting global values.
            if args.type is None:
                origin = args.o
                if args.o is None:
                    origin = input("Git origin for deployment : ")

                Utility.update_config(config_file, {'global':{'git':{'origin':origin}}})
                logging.info("Global configs updated.")

            # If adding or updating configs.
            elif args.type == 'add' or  args.type == 'update':
                if args.d is None:
                    cls.parser.error("-d argument is required. Check usage.")

                # Sanitize values.
                configs, flag, msg = DeploymentConfig.validate_configs(args)

                if flag:
                    cls.parser.error(msg)
                else:
                    if args.type == 'update':
                        Utility.update_config(config_file, configs)
                    if args.type == 'add':
                        Utility.add_configs(['deployment', args.d],config_file, configs)

            # Showing configs
            elif args.type == 'show':
                Utility.print_file(Utility.project_config(config_file))

            # Unsupported argument type.
            else:
                cls.parser.error("Unsupported command argument {}. See usage.".format(args.type))

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
            },

            {
                'func': cls.config,
                'parser': 'config',
                'help': 'Setup configs for your project. Read documentation for argument types.\n'+
                        'TYPES:\n'+
                        'Argument\n'+
                        '-i: Prompt for input\n'+
                        '   add - add a config for your deployment.\n'+
                        '   update - update an existing config for your deployment.\n'+
                        '       Arguments:\n'+
                        '           -d : Deployment Type\n'+
                        '           -p : Project\n'+
                                    DeploymentConfig.CONFIG_DETAILS+
                        '   If None is provided\n'+
                        '       Arguments:\n'+
                        '           -p : Project\n'+
                        '           -o : Set git origin for deployment\n'+
                        '   show -  Show the config file on console'
                        ,
                'args': [
                    ['type'],
                    ['-d', {'choices': Utility.read_meta()['deployment']}],
                    ['-o'],
                    ['-p'],
                    ['-n'],
                    ['-e'],
                    ['-c'],
                    ['-t']
                ]

            }

        )
        return subparsers


    @classmethod
    def validate_project(cls, args):
        try:
            # Check if -p <arg> is a project or if the pwd is a project.
            config_file = None

            # if -p is present
            if args is not None:
                # -p <arg> does not have a config file.
                if not os.path.exists(Utility.project_config(args)):
                    cls.parser.error("{} is not an afctl project. Config file does not exists".format(args))
                    logging.error("Not a project.")
                else:
                    # -p <arg> has a config file.
                    config_file = args
                    logging.info("{} is a valid afctl project".format(args))

            # -p <arg> is not present so lets check pwd
            else:
                pwd = os.getcwd()
                # If any parent of pwd contains afctl_project_meta.yml. If so then it should be the project.
                config_file = Utility.find_project(pwd)
                if config_file is None:
                    # Could not find afctl_project_meta.yml
                    cls.parser.error("{} is not an afctl project.".format(pwd))
                    logging.error("Not a project.")
                else:
                    # Check is the dir containing afctl_project_meta.yml has a config file
                    if not os.path.exists(Utility.project_config(config_file)):
                        cls.parser.error("Config file does not exists for {}".format(config_file))
                        logging.error("Not a project.")

            return config_file
        except Exception as e:
            raise AfctlParserException(e)
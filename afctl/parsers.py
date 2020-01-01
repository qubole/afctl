__author__ = 'Aaditya Sharma'

import argparse
import os
from afctl import __version__
from afctl.utils import Utility
from afctl.exceptions import AfctlParserException
import subprocess
from afctl.plugins.deployments.deployment_config import DeploymentConfig
from afctl.parser_helpers import ParserHelpers


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

            files = ParserHelpers.init_file_name(args.name)

            if not os.path.exists(files['config_dir']):
                os.mkdir(files['config_dir'])

            if os.path.exists(files['main_dir']) and os.path.exists(files['config_file']):
                cls.parser.error("Project already exists. Please delete entry under afctl_congfis after removing\
                                the project from the current directory.")

            print("Initializing new project...")

            # STEP - 1: Create parent dir
            if args.name != '.':
                os.mkdir(files['main_dir'])

            # STEP - 2: create files and dirs
            sub_file, dirs, sub_dir = ParserHelpers.init_files(files)

            #STEP - 3: create config file
            subprocess.run(['cp', '{}/plugins/deployments/deployment_config.yml'.format(os.path.dirname(os.path.abspath(__file__))),
                            files['config_file']])
            subprocess.run(['cp', '{}/templates/gitignore.txt'.format(os.path.dirname(os.path.abspath(__file__))),
                            sub_file['.gitignore']])

            #STEP - 4: Add git origin.
            ParserHelpers.add_git_origin(files)

            # STEP - 5: Generate files if required by deployments.
            DeploymentConfig.generate_dirs(files['main_dir'], files['project_name'])

            print("New project initialized successfully.")

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def list(cls, args):
        try:
            print("Available {} :".format(args.type))
            print('\n'.join(map(str, Utility.read_meta()[args.type])))

        except Exception as e:
            raise AfctlParserException(e)

    @classmethod
    def config(cls, args):
        try:
            config_file = cls.validate_project(args.p)

            if config_file is None:
                cls.parser.error("Invalid project.")

            # Setting global values.
            if args.type == "global":
                origin = args.o
                if args.o is None:
                    origin = input("Git origin for deployment : ")
                if origin != '':
                    Utility.update_config(config_file, {'global':{'git':{'origin':origin}}})

            # If adding or updating configs.
            elif args.type == 'add' or  args.type == 'update':
                if args.d is None:
                    cls.parser.error("-d argument is required. Check usage. Run 'afctl config -h'")

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


        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def deploy(cls, args):
        try:

            # args.p will always be None
            config_file = cls.validate_project(None)
            if config_file is None:
                cls.parser.error("Invalid project.")

            flag, msg = DeploymentConfig.deploy_project(args, config_file)

            if flag:
                print("Deployment failed. See usage. Run 'afctl deploy -h'")
                cls.parser.error(msg)

            print("Deployment successful on {}".format(args.type))

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def generate(cls, args):

        try:
            config_file = cls.validate_project(None)
            if config_file is None:
                cls.parser.error("Invalid project.")

            if args.type == "dag":
                Utility.generate_dag_template(config_file, args.n)

            print("Template generated successfully.")

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
                        '   add - add a config for your deployment.\n'+
                        '   update - update an existing config for your deployment.\n'+
                        '       Arguments:\n'+
                        '           -d : Deployment Type\n'+
                        '           -p : Project\n'+
                                    DeploymentConfig.CONFIG_DETAILS+
                        '   global\n'+
                        '       Arguments:\n'+
                        '           -p : Project\n'+
                        '           -o : Set git origin for deployment\n'+
                        '   show -  Show the config file on console\n'+
                        '       No arguments.'
                        ,
                'args': [
                    ['type', {'choices':['add', 'update', 'show', 'global']}],
                    ['-d', {'choices': ['qubole']}],
                    ['-o'],
                    ['-p'],
                    ['-n'],
                    ['-e'],
                    ['-c']
                ]

            },

            {
                'func': cls.deploy,
                'parser': 'deploy',
                'help': 'Deploy your afctl project on the preferred platform.\n'+
                        'TYPES:\n'+
                            DeploymentConfig.DEPLOY_DETAILS
                        ,
                'args': [
                    ['type', {'choices':Utility.read_meta()['deployment']}],
                    ['-d',{'action':'store_true'}],
                    ['-n']
                ]
            },

            {
                'func': cls.generate,
                'parser': 'generate',
                'help': 'Generators',
                'args': [
                    ['type', {'choices':['dag']}],
                    ['-n', {'required':'True'}]
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
                else:
                    # -p <arg> has a config file.
                    config_file = args

            # -p <arg> is not present so lets check pwd
            else:
                pwd = os.getcwd()
                # If any parent of pwd contains .afctl_project. If so then it should be the project.
                config_file = Utility.find_project(pwd)
                if config_file is None:
                    # Could not find .afctl_project
                    cls.parser.error("{} is not an afctl project.".format(pwd))
                else:
                    # Check is the dir containing .afctl_project has a config file
                    if not os.path.exists(Utility.project_config(config_file)):
                        cls.parser.error("Config file does not exists for {}".format(config_file))

            return config_file
        except Exception as e:
            raise AfctlParserException(e)
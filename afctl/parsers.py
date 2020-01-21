__author__ = 'Aaditya Sharma'

import argparse
import os
from afctl import __version__
from afctl.utils import Utility
from afctl.exceptions import AfctlParserException
import subprocess
from afctl.plugins.deployments.deployment_config import DeploymentConfig
from afctl.parser_helpers import ParserHelpers
from termcolor import colored


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
                cls.parser.error(colored("Project already exists. Please delete entry under /home/.afctl_congfis", 'red'))

            print(colored("Initializing new project...", 'green'))

            # New afctl project
            ParserHelpers.generate_project(args, files)

            print(colored("New project initialized successfully.", 'green'))

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def list(cls, args):
        try:
            print(colored("Available {} :".format(args.type), 'green'))
            print('\n'.join(map(str, Utility.read_meta()[args.type])))

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def config(cls, args):
        try:
            config_file = cls.validate_project(args.p)

            if config_file is None:
                cls.parser.error(colored("Invalid project.", 'red'))

            cls.act_on_configs(args, config_file)

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def deploy(cls, args):
        try:
            # args.p will always be None
            config_file = cls.validate_project(None)
            if config_file is None:
                cls.parser.error(colored("Invalid project.", 'red'))

            flag, msg = DeploymentConfig.deploy_project(args, config_file)

            if flag:
                print(colored("Deployment failed. See usage. Run 'afctl deploy -h'", 'yellow'))
                cls.parser.error(colored(msg, 'red'))

            print(colored("Deployment successful on {}".format(args.type), 'green'))

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def generate(cls, args):

        try:
            project_name = cls.validate_project(None)
            if project_name is None:
                cls.parser.error(colored("Invalid project.", 'red'))

            parent_dir = Utility.is_afctl_project(os.getcwd())
            if args.type == "dag":
                path = "{}/{}/dags".format(parent_dir, project_name)
                if args.m is not None:
                    path = os.path.join(path, args.m)
                    if not os.path.exists(path):
                        cls.parser.error(colored("The specified module does not exists", 'red'))
                Utility.generate_dag_template(project_name, args.n, path)

            elif args.type == "module":
                path = "{}/{}/dags/{}".format(parent_dir, project_name, args.n)
                test_path = "{}/tests/{}".format(parent_dir, args.n)
                mod_val = subprocess.call(['mkdir', path])
                test_val = subprocess.call(['mkdir', test_path])
                if mod_val != 0 or test_val != 0:
                    cls.parser.error(colored("Unable to generate.", 'red'))

            print(colored("Generated successfully.", 'green'))

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
                        '           -t : Set personal access token\n'+
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
                    ['-c'],
                    ['-t']
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
                'help': 'Generators\n'+
                        '-n : Name of the dag file or the module\n'+
                        '-m : Name of module where you want to generate a dag file\n',
                'args': [
                    ['type', {'choices':['dag', 'module']}],
                    ['-n', {'required':'True'}],
                    ['-m']
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
                    cls.parser.error(colored("{} is not an afctl project. Config file does not exists".format(args), 'red'))
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
                    cls.parser.error(colored("{} is not an afctl project.".format(pwd), 'red'))
                else:
                    # Check is the dir containing .afctl_project has a config file
                    if not os.path.exists(Utility.project_config(config_file)):
                        cls.parser.error(colored("Config file does not exists for {}".format(config_file), 'red'))

            return config_file
        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def act_on_configs(cls, args, config_file):
        try:

            # Setting global values.
            if args.type == "global":
                origin = args.o
                token = args.t
                if args.o is None and args.t is None:
                    origin = input("Git origin for deployment : ")
                    token = input("Personal access token : ")

                if origin != '' and origin is not None:
                    Utility.update_config(config_file, {'global':{'git':{'origin':origin}}})

                if token != '' and token is not None:
                    Utility.update_config(config_file, {'global':{'git':{'access-token':token}}})

            # If adding or updating configs.
            elif args.type == 'add' or  args.type == 'update':
                if args.d is None:
                    cls.parser.error(colored("-d argument is required. Check usage. Run 'afctl config -h'", 'red'))

                # Sanitize values.
                configs, flag, msg = DeploymentConfig.validate_configs(args)
                if flag:
                    cls.parser.error(colored(msg, 'red'))
                else:
                    if args.type == 'update':
                        Utility.update_config(config_file, configs)
                    if args.type == 'add':
                        Utility.add_configs(['deployment', args.d],config_file, configs)

            # Showing configs
            elif args.type == 'show':
                Utility.print_file(Utility.project_config(config_file))

        except Exception as e:
            AfctlParserException(e)
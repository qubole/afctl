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
            files = ParserHelpers.get_project_file_names(args.name)

            if not os.path.exists(files['config_dir']):
                os.mkdir(files['config_dir'])

            if os.path.exists(files['main_dir']) and os.path.exists(files['config_file']):
                cls.parser.error(colored("Project already exists. Please delete entry under /home/.afctl_congfis", 'red'))

            print(colored("Initializing new project...", 'green'))

            # New afctl project
            flag = ParserHelpers.generate_project(args, files)

            if flag:
                print(colored("Unable to initialize project.", 'red'))
            else:
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
            project_name, project_path = cls.validate_project()

            if project_name is None:
                cls.parser.error(colored("Invalid project.", 'red'))

            cls.act_on_configs(args, project_name)

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def deploy(cls, args):
        try:
            # args.p will always be None
            project_name, project_path = cls.validate_project()
            if project_name is None:
                cls.parser.error(colored("Invalid project.", 'red'))

            flag, msg = DeploymentConfig.deploy_project(args, project_name, project_path)

            if flag:
                print(colored("Deployment failed. See usage. Run 'afctl deploy -h'", 'yellow'))
                cls.parser.error(colored(msg, 'red'))

            print(colored("Deployment successful on {}".format(args.type), 'green'))

        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def generate(cls, args):

        try:
            project_name, project_path = cls.validate_project()
            if project_name is None:
                cls.parser.error(colored("Invalid project.", 'red'))

            if args.type == "dag":
                path = "{}/{}/dags".format(project_path, project_name)
                if args.m is not None:
                    path = os.path.join(path, args.m)
                    if not os.path.exists(path):
                        cls.parser.error(colored("The specified module does not exists", 'red'))
                Utility.generate_dag_template(project_name, args.n, path)

            elif args.type == "module":
                path = "{}/{}/dags/{}".format(project_path, project_name, args.n)
                test_path = "{}/tests/{}".format(project_path, args.n)
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
                    ['name', {'help':'Name of your airflow project'}],
                    ['-v', {'help': 'Airflow version for your project'}]
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
                    ['-t'],
                    ['-v']
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
    def validate_project(cls):
        try:
            project_name = None
            project_path = None
            pwd = os.getcwd()
            # If any parent of pwd contains .afctl_project. If so then it should be the project.
            project = Utility.find_project(pwd)
            if project is None:
                # Could not find .afctl_project
                cls.parser.error(colored("{} is not an afctl project.".format(pwd), 'red'))
            else:
                # Check is the dir containing .afctl_project has a config file
                project_name = project[0]
                project_path = project[1]
                if not os.path.exists(Utility.project_config(project_name)):
                    cls.parser.error(colored("Config file does not exists for {}".format(project_name), 'red'))

            return project_name, project_path
        except Exception as e:
            raise AfctlParserException(e)


    @classmethod
    def act_on_configs(cls, args, project_name):
        try:
            # Setting global values.
            if args.type == "global":
                origin = args.o
                token = args.t
                version = args.v
                if args.o is None and args.t is None and args.v is None:
                    origin = input("Git origin for deployment : ")
                    token = input("Personal access token : ")
                    version = input("Input airflow version : ")

                if origin != '' and origin is not None:
                    Utility.update_config(project_name, {'global':{'git':{'origin':origin}}})

                if token != '' and token is not None:
                    Utility.update_config(project_name, {'global':{'git':{'access-token':token}}})

                if version != '' and version is not None:
                    Utility.update_config(project_name, {'global': {'airflow_version': version}})

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
                        Utility.update_config(project_name, configs)
                    if args.type == 'add':
                        Utility.add_configs(['deployment', args.d], project_name, configs)

            # Showing configs
            elif args.type == 'show':
                Utility.print_file(Utility.project_config(project_name))

        except Exception as e:
            AfctlParserException(e)
from afctl.utils import Utility
import os
import subprocess
from termcolor import colored
from afctl.plugins.deployments.deployment_config import DeploymentConfig
from afctl.exceptions import AfctlParserException

class ParserHelpers():

    @staticmethod
    def init_file_name(name):
        try:
            pwd = os.getcwd()
            main_dir = pwd if name == '.' else os.path.join(pwd, name.lstrip('/').rstrip('/'))
            project_name = os.path.basename(main_dir)
            config_dir = Utility.CONSTS['config_dir']
            config_file = Utility.project_config(project_name)
            sub_files = ['.afctl_project', '.gitignore']
            sub_dirs = [project_name, 'deployments', 'migrations', 'plugins', 'tests']
            project_dirs = ['dags', 'commons']

            return {
                'main_dir': main_dir,
                'project_name': project_name,
                'config_dir': config_dir,
                'config_file':config_file,
                'sub_files': sub_files,
                'sub_dirs': sub_dirs,
                'project_dirs': project_dirs
            }

        except Exception as e:
            raise AfctlParserException(e)


    @staticmethod
    def add_git_config(files):
        try:
            origin = subprocess.run(['git', '--git-dir={}'.format(os.path.join(files['main_dir'], '.git')), 'config',
                                     '--get', 'remote.origin.url'],stdout=subprocess.PIPE)
            origin = origin.stdout.decode('utf-8')[:-1]
            if origin == '':
                subprocess.run(['git', 'init', files['main_dir']])
                print(colored("Git origin is not set for this repository. Run 'afctl config global -o <origin>'", 'yellow'))
            else:
                print("Updating git origin.")
                Utility.update_config(files['project_name'], {'global':{'git':{'origin':origin}}})
                print("Setting origin as : {}".format(origin))
            print(colored("Set personal access token for Github. Run 'afctl config global -t <token>'", 'yellow'))
        except Exception as e:
            raise AfctlParserException(e)


    @staticmethod
    def init_files(files):
        try:
            sub_file = Utility.create_files([files['main_dir']], files['sub_files'])
            dirs = Utility.create_dirs([files['main_dir']], files['sub_dirs'])
            project_dirs = Utility.create_dirs([dirs[files['project_name']]], files['project_dirs'])
            return sub_file, dirs, project_dirs

        except Exception as e:
            raise AfctlParserException(e)


    @staticmethod
    def init_project(files):
        try:
            # STEP - 1: create files and dirs
            sub_file, dirs, project_dirs = ParserHelpers.init_files(files)

            #STEP - 2: create config file
            ParserHelpers.generate_config_file(files)

            subprocess.run(['cp', '{}/templates/gitignore.txt'.format(os.path.dirname(os.path.abspath(__file__))),
                            sub_file['.gitignore']])

        except Exception as e:
            raise AfctlParserException(e)


    @staticmethod
    def generate_config_file(files):
        try:
            subprocess.run(['cp', '{}/plugins/deployments/deployment_config.yml'.format(os.path.dirname(os.path.abspath(__file__))),
                            files['config_file']])

            DeploymentConfig.generate_dirs(files['main_dir'], files['project_name'])
            ParserHelpers.add_git_config(files)

        except Exception as e:
            raise AfctlParserException(e)


    @staticmethod
    def generate_project(args, files):
        try:
            if args.name != '.':
                os.mkdir(files['main_dir'])
                ParserHelpers.init_project(files)
            else:
                # Initialising project in existing directory
                project_parent_dir = Utility.is_afctl_project(os.getcwd())
                if project_parent_dir is None:
                    # Not an afctl project. Generate all directories.
                    ParserHelpers.init_project(files)
                else:
                    # Since its an afctl project. Just populate the config files.
                    ParserHelpers.generate_config_file(files)

        except Exception as e:
            raise AfctlParserException(e)

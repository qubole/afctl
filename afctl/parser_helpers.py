from afctl.utils import Utility
import os
import subprocess

class ParserHelpers():

    @staticmethod
    def init_file_name(name):
        pwd = os.getcwd()
        main_dir = pwd if name == '.' else os.path.join(pwd, name.lstrip('/').rstrip('/'))
        project_name = os.path.basename(main_dir)
        config_dir = Utility.CONSTS['config_dir']
        config_file = Utility.project_config(project_name)
        sub_files = ['.afctl_project', '.gitignore']
        sub_dirs = [project_name, 'deployments']
        project_init_file = ['__init__.py']

        return {
            'main_dir': main_dir,
            'project_name': project_name,
            'config_dir': config_dir,
            'config_file':config_file,
            'sub_files': sub_files,
            'sub_dirs': sub_dirs,
            'project_init_file': project_init_file
        }


    @staticmethod
    def add_git_origin(files):
        origin = subprocess.run(['git', '--git-dir={}'.format(os.path.join(files['main_dir'], '.git')), 'config',
                                 '--get', 'remote.origin.url'],stdout=subprocess.PIPE)
        origin = origin.stdout.decode('utf-8')[:-1]
        if origin == '':
            subprocess.run(['git', 'init', files['main_dir']])
            print("Git origin is not set for this repository. Run 'afctl config global -o <origin>'")
        else:
            Utility.update_config(files['project_name'], {'global':{'git':{'origin':origin}}})
            print("Setting origin as : {}".format(origin))


    @staticmethod
    def init_files(files):
        sub_file = Utility.create_files([files['main_dir']], files['sub_files'])
        dirs = Utility.create_dirs([files['main_dir']], files['sub_dirs'])
        sub_dir = Utility.create_files([dirs[files['sub_dirs'][0]]], files['project_init_file'])
        return sub_file, dirs, sub_dir
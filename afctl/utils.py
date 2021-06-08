import os
import itertools
import pathlib
import yaml
from afctl.exceptions import AfctlUtilsException
from afctl.templates.dag_template import dag_template
from termcolor import colored

SEP = os.path.sep

class Utility():

    CONSTS = {
        'config_dir': os.path.join(os.path.expanduser("~"), '.afctl_config')
    }

    @staticmethod
    def create_dirs(parent, child):
        try:
            dirs = {}
            for dir1, dir2 in itertools.product(parent, child):
                target = os.path.join(dir1, dir2)
                if not os.path.exists(target):
                    os.makedirs(target)
                else:
                    print("{} already exists. Skipping.".format(dir2))
                dirs[dir2] = target
            return dirs
        except Exception as e:
            raise AfctlUtilsException(e)


    @staticmethod
    def create_files(parent, child):
        try:
            files = {}
            for dir1, dir2 in itertools.product(parent, child):
                if not os.path.exists(os.path.join(dir1, dir2)):
                    pathlib.Path(os.path.join(dir1, dir2)).touch()
                else:
                    print("{} already exists. Skipping.".format(dir2))
                files[dir2] = os.path.join(dir1, dir2)
            return files
        except Exception as e:
            raise AfctlUtilsException(e)


    @staticmethod
    def read_meta():
        try:
            with open("{}/{}".format(os.path.dirname(os.path.abspath(__file__)), 'meta.yml')) as file:
                data = yaml.full_load(file)
            operators = "" if data['operators'] is None else data['operators'].split(' ')
            hooks = "" if data['hooks'] is None else data['hooks'].split(' ')
            sensors = "" if data['sensors'] is None else data['sensors'].split(' ')
            deployment = "" if data['deployment'] is None else data['deployment'].split(' ')

            return {'operators':operators, 'hooks':hooks, 'sensors':sensors, 'deployment':deployment}

        except Exception as e:
            raise AfctlUtilsException(e)


    @staticmethod
    def project_config(file):
        return "{}.yml".format(os.path.join(Utility.CONSTS['config_dir'], file))


    @staticmethod
    def print_file(file):
        try:
            with open(file) as fh:
                print(fh.read())
        finally:
            fh.close()

    @staticmethod
    def update_config(file, config):
        try:
            path = Utility.project_config(file)
            if not os.path.exists(path):
                print(colored("Project's config file does not exists", 'red'))
                raise Exception("Project's config file does not exists")

            with open(path) as file:
                crawler = yaml.full_load(file)
            Utility.crawl_config(crawler, config)
            with open(path, 'w') as file:
                yaml.dump(crawler, file, default_flow_style=False, sort_keys=False)

            print(colored("Configurations updated.", 'green'))
        except Exception as e:
            raise AfctlUtilsException(e)


    @staticmethod
    def crawl_config(crawler, config):
        try:
            for k,v in config.items():
                if isinstance(v, str):
                    crawler[k] = v
                else:
                    Utility.crawl_config(crawler[k], v)
        except Exception as e:
            raise AfctlUtilsException(e)


    @staticmethod
    def find_project(pwd):
        dirs = pwd.split(SEP)
        for i in range(len(dirs), 0, -1):
            path = SEP.join(dirs[:i])
            if os.path.exists(os.path.join(path, '.afctl_project')):
                return [dirs[i-1], path]
        return None

    @staticmethod
    def add_configs(config_parents, config_file, configs):
        try:
            path = Utility.project_config(config_file)
            if not os.path.exists(path):
                print(colored("Project's config file does not exists", 'red'))
                raise Exception("Project's config file does not exists")

            with open(path) as file:
                crawler = yaml.full_load(file)

            obj = crawler
            for k in config_parents[:-1]:
                obj = obj[k]

            for k,v in configs.items():
                if obj[ config_parents[-1]] is None:
                    obj[ config_parents[-1]] = {}
                obj[ config_parents[-1]][k] = v

            with open(path, 'w') as file:
                yaml.dump(crawler, file, default_flow_style=False, sort_keys=False)

            print(colored("New configuration added successfully.", 'green'))
        except Exception as e:
            raise AfctlUtilsException(e)

    @staticmethod
    def generate_dag_template(project_name, name, path):
        dag_file = dag_template(name, project_name)
        with open('{}/{}_dag.py'.format(path, name), 'w') as file:
            file.write(dag_file)

import os
import subprocess
import itertools

PROJECT_NAME = 'test_project'
PROJECT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), '.afctl_config')


class DummyArgParse:

    def __init__(self, type=None, origin=None, token=None, version=None):
        self.type = type
        self.o = origin
        self.t = token
        self.v = version


def clean_up(project_name, config_dir):
    if os.path.exists(project_name):
        subprocess.run(['rm', '-rf', project_name])

    if os.path.exists(config_dir):
        subprocess.run(['rm', '-rf', config_dir])


def check_paths(parent, child):
    for dir1, dir2 in itertools.product(parent, child):
        if not os.path.exists(os.path.join(dir1, dir2)):
            return False
    return True


def create_path_and_clean(parent, child):
    for dir1, dir2 in itertools.product(parent, child):
        dir_path = os.path.join(dir1, dir2)
        if os.path.exists(dir_path):
            subprocess.run(['rm', '-rf', dir_path])

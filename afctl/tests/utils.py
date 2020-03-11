import os
import subprocess
import itertools

PROJECT_NAME = 'test_project'
PROJECT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), '.afctl_config')


class DummyArgParse:

    def __init__(self, type=None, origin=None, token=None, version=None, env=None, cluster=None, name=None):
        self.type = type
        self.o = origin
        self.t = token
        self.v = version
        self.e = env
        self.c = cluster
        self.n = name


def clean_up(project_file):
    if os.path.exists(project_file):
        subprocess.run(['rm', '-rf', project_file])


def check_paths(parent, child):
    for dir1, dir2 in itertools.product(parent, child):
        if not os.path.exists(os.path.join(dir1, dir2)):
            return False
    return True


def create_path_and_clean(parent, child):
    for dir1, dir2 in itertools.product(parent, child):
        dir_path = os.path.join(dir1, dir2)
        clean_up(dir_path)

import os
import subprocess
import itertools

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

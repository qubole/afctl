import os
import itertools
import subprocess

class Utility():

    @staticmethod
    def create_dirs(parent, child):
        dirs = {}
        for dir1, dir2 in itertools.product(parent, child):
            os.mkdir(os.path.join(dir1, dir2))
            dirs[dir2] = os.path.join(dir1, dir2)
        return dirs

    @staticmethod
    def create_files(parent, child):
        files = {}
        for dir1, dir2 in itertools.product(parent, child):
            subprocess.run(['touch', os.path.join(dir1, dir2)])
            files[dir2] = os.path.join(dir1, dir2)
        return files

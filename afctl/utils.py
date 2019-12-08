import os
import itertools

class Utility():

    @staticmethod
    def create_dirs(parent, child):
        for dir1, dir2 in itertools.product(parent, child):
            os.mkdir(os.path.join(dir1, dir2))

    @staticmethod
    def create_files(parent, child):
        for dir1, dir2 in itertools.product(parent, child):
            os.system("touch {}".format(os.path.join(dir1, dir2)))

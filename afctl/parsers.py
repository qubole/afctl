import argparse
import yaml
import sys
import os

class Parser():


    def setup_parser(self):
        parser = argparse.ArgumentParser(description="A CLI tool to make deployment of airflow projects faster")
        # parser.add_argument("-v", "--version", action="store_true")  learn the standard way to add version to python package
        new_parser = parser.add_subparsers()
        sub_parser = new_parser.add_parser("init", help="Create a boilerplate code for your airflow project")
        sub_parser.set_defaults(func=self.create_project)
        sub_parser.add_argument("name", help="Name of your airflow project")
        sub_parser.add_argument("plugin", help="Add plugin to your project", choices=self.plugins)
        sub_parser = new_parser.add_parser("list", help="Get list of operators, sensors, plugins, hooks.")
        sub_parser.set_defaults(func=self.list)
        sub_parser.add_argument("type", choices=self.choices)
        return parser

    def create_project(self, args):
        pass

    def list(self, args):
        print("Available {} :".format(args.type))
        vals = eval("self.{}".format(args.type))
        print('\n'.join(map(str, vals)))

    def __init__(self):
        try:
            with open("{}/{}".format(os.path.dirname(os.path.abspath(__file__)), 'meta.yml')) as file:
                self.data = yaml.full_load(file)

            self.choices = [k for k in self.data]
            self.operators = self.data['operators'].split(' ')
            self.hooks = self.data['hooks'].split(' ')
            self.sensors = self.data['sensors'].split(' ')
            self.plugins = self.data['plugins'].split(' ')
        except:
            sys.exit(3)



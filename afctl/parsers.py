import argparse

class Parser():

    @classmethod
    def setup_parser(cls):
        cls.parser = argparse.ArgumentParser(description="A CLI tool to make deployment of airflow projects faster")
        cls.parser.add_argument("-v", "--version", action="store_true")  #learn the standard way to add version to python package
        cls.new_parser = cls.parser.add_subparsers()
        cls.sub_parser = cls.new_parser.add_parser("init", help="Create a boilerplate code for your airflow project")
        cls.sub_parser.set_defaults(func=cls.create_project)
        cls.sub_parser.add_argument("name", help="Name of your airflow project")
        cls.sub_parser.add_argument("plugin", help="Add plugin to your project")
        cls.sub_parser = cls.new_parser.add_parser("list", help="Get list of operators, sensors, plugins, hooks.")
        cls.sub_parser.set_defaults(func=cls.list)
        cls.sub_parser.add_argument("type", choices=["sensors", "operators", "hooks", "plugins"])
        return cls.parser

    @classmethod
    def create_project(cls, args):
        pass

    @classmethod
    def list(cls, args):
        pass

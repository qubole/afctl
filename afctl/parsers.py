import argparse


def setup_parser():
    parser = argparse.ArgumentParser(description="A CLI tool to make deployment of airflow projects faster")
    parser.add_argument("-v", "--version", action="store_true")  #learn the standard way to add version to python package
    new_parser = parser.add_subparsers()
    sub_parser = new_parser.add_parser("init", help="Create a boilerplate code for your airflow project")
    sub_parser.add_argument("name", help="Name of your airflow project")
    sub_parser.add_argument("plugin", help="Add plugin to your project")
    sub_parser = new_parser.add_parser("list", help="Get list of operators, sensors, plugins, hooks.")
    sub_parser.add_argument("type", choices=["sensors", "operators", "hooks", "plugins"])
    return parser


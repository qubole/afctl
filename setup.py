from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="afctl",
    version="0.1",
    url="TODO",
    author="TODO",
    author_email="TODO",
    description="Python commandline tool to make deployment of Airflow projects easier.",
    packages=find_packages(),
    package_data={'afctl': ['meta.yml']},
    entry_points={
        'console_scripts': ['afctl=afctl.command_line:main'],
    },
    install_requires=required,
)

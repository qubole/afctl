from setuptools import setup, find_packages
from os import path
import versioneer

with open('requirements.txt') as f:
    required = f.read().splitlines()

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="afctl",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/qubole/afctl",
    author="Qubole",
    author_email="dev@qubole.com",
    description="Python commandline tool to make deployment of Airflow projects easier.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="airflow cli deployment",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['afctl=afctl.command_line:main'],
    },
    install_requires=required,
)

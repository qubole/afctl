from setuptools import setup, find_packages
import os
import versioneer

with open('requirements.txt') as f:
    required = f.read().splitlines()

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="afctl",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/qubole/afctl",
    author="Qubole",
    author_email="dev@qubole.com",
    description="Python commandline tool to make deployment of Airflow projects easier.",
    long_description=read('README.md'),
    keywords="airflow cli deployment",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['afctl=afctl.command_line:main'],
    },
    install_requires=required,
)

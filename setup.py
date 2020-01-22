from setuptools import setup, find_packages
import versioneer

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="afctl",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/qubole/afctl",
    author="Qubole",
    author_email="dev@qubole.com",
    description="Python commandline tool to make deployment of Airflow projects easier.",
    keywords="airflow cli deployment",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['afctl=afctl.command_line:main'],
    },
    install_requires=required,
)

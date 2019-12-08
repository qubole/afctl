from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="afctl",
    #version=versioneer.get_version(),
    #cmdclass=versioneer.get_cmdclass(),
    url="TODO",
    author="TODO",
    author_email="TODO",
    description="Python commandline tool to make deployment of Airflow projects easier.",
    packages=find_packages(),
    package_data={},
    entry_points={
        'console_scripts': ['afctl=afctl.command_line:main'],
    },
    install_requires=required,
)

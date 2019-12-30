from afctl.plugins.deployments.base_deployment_config import BaseDeploymentConfig
import os
import yaml
from afctl.utils import Utility
import subprocess

# Yaml Structure
#   deployment:
#       docker:
#           compose:

class DockerDeploymentConfig(BaseDeploymentConfig):
    CONFIG_PARSER_USAGE = \
        '            [ docker ]\n'+\
        '               Cannot add/update configs.\n'

    DEPLOY_PARSER_USAGE = \
        '   [docker] - Deploy your project to local docker.\n'+ \
        '       Arguments:\n'+ \
        '           -d : To run in daemon mode\n'


    @classmethod
    def generate_dirs(cls, main_dir, project_name):
        file_path = os.path.dirname(os.path.abspath(__file__))
        composer_file = os.path.join(file_path, 'afctl-docker-compose.yml')
        os.system("cp {} {}/deployments/{}-docker-compose.yml".format(composer_file, main_dir, project_name))
        Utility.update_config(project_name, {'deployment':{'docker':{'compose': "{}/deployments/{}-docker-compose.yml".format(main_dir, project_name)}}})

        # Change dags directory in volume



    @classmethod
    def deploy_project(cls, args, config_file):

        print("Deploying afctl project to docker")

        with open(Utility.project_config(config_file)) as file:
            config = yaml.full_load(file)

        val = subprocess.call(['docker', 'info'])
        if val != 0:
            return True, "Docker is not running. Please start docker."

        if args.d:
            os.system("docker-compose -f {} up -d".format(config['deployment']['docker']['compose']))
        else:
            os.system("docker-compose -f {} up ".format(config['deployment']['docker']['compose']))

        return False, ""


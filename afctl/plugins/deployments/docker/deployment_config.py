from afctl.plugins.deployments.base_deployment_config import BaseDeploymentConfig
from afctl.exceptions import AfctlDeploymentException
import os
import yaml
from afctl.utils import Utility
import subprocess

# Yaml Structure
#   deployment:
#       local:
#           compose:

class DockerDeploymentConfig(BaseDeploymentConfig):
    CONFIG_PARSER_USAGE = \
        '            [ local ]\n'+\
        '               Cannot add/update configs.\n'

    DEPLOY_PARSER_USAGE = \
        '   [local] - Deploy your project to local docker.\n'+ \
        '       Arguments:\n'+ \
        '           -d : To run in daemon mode\n'


    @classmethod
    def generate_dirs(cls, main_dir, project_name):
        try:
            file_path = os.path.dirname(os.path.abspath(__file__))
            composer_file = os.path.join(file_path, 'afctl-docker-compose.yml')
            os.system("cp {} {}/deployments/{}-docker-compose.yml".format(composer_file, main_dir, project_name))
            print("Updating docker compose.")
            Utility.update_config(project_name, {'deployment':{'local':{'compose': "{}/deployments/{}-docker-compose.yml".format(main_dir, project_name)}}})

        # Change dags directory in volume
        except Exception as e:
            raise AfctlDeploymentException(e)


    @classmethod
    def deploy_project(cls, args, config_file):

        try:

            print("Deploying afctl project to local")

            with open(Utility.project_config(config_file)) as file:
                config = yaml.full_load(file)

            val = subprocess.call(['docker', 'info'])
            if val != 0:
                return True, "Docker is not running. Please start docker."

            if args.d:
                os.system("docker-compose -f {} up -d".format(config['deployment']['local']['compose']))
            else:
                os.system("docker-compose -f {} up ".format(config['deployment']['local']['compose']))

            return False, ""

        except Exception as e:
            raise AfctlDeploymentException(e)


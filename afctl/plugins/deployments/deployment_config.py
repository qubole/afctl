from afctl.plugins.deployments.base_deployment_config import BaseDeploymentConfig
from afctl.plugins.deployments.qubole.deployment_config import QuboleDeploymentConfig
from afctl.plugins.deployments.docker.deployment_config import DockerDeploymentConfig

from afctl.exceptions import AfctlDeploymentException

class DeploymentConfig(BaseDeploymentConfig):
    # Just append configs for other deployments here.
    CONFIG_DETAILS = QuboleDeploymentConfig.CONFIG_PARSER_USAGE+\
                     DockerDeploymentConfig.CONFIG_PARSER_USAGE

    DEPLOY_DETAILS = QuboleDeploymentConfig.DEPLOY_PARSER_USAGE+\
                     DockerDeploymentConfig.DEPLOY_PARSER_USAGE

    @classmethod
    def generate_dirs(cls, main_dir, project_name):
        QuboleDeploymentConfig.generate_dirs(main_dir, project_name)
        DockerDeploymentConfig.generate_dirs(main_dir, project_name )

    @classmethod
    def validate_configs(cls, args):
        try:

            if args.d == 'qubole':
                return QuboleDeploymentConfig.validate_configs(args)

        except Exception as e:
            raise AfctlDeploymentException(e)


    @classmethod
    def deploy_project(cls, args, config_file):
        try:

            if args.type == "local":
                return DockerDeploymentConfig.deploy_project(args, config_file)

            if args.type == "qubole":
                return QuboleDeploymentConfig.deploy_project(args, config_file)

        except Exception as e:
            raise AfctlDeploymentException(e)
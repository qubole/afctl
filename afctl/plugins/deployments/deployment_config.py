from afctl.plugins.deployments.base_deployment_config import BaseDeploymentConfig
from afctl.plugins.deployments.qubole.deployment_config import QuboleDeploymentConfig
from afctl.plugins.deployments.docker.deployment_config import DockerDeploymentConfig
from afctl.plugins.deployments.scp.deployment_config import ScpDeploymentConfig

from afctl.exceptions import AfctlDeploymentException

class DeploymentConfig(BaseDeploymentConfig):
    # Just append configs for other deployments here.
    CONFIG_DETAILS = QuboleDeploymentConfig.CONFIG_PARSER_USAGE+\
                     DockerDeploymentConfig.CONFIG_PARSER_USAGE+\
                     ScpDeploymentConfig.CONFIG_PARSER_USAGE

    DEPLOY_DETAILS = QuboleDeploymentConfig.DEPLOY_PARSER_USAGE+\
                     DockerDeploymentConfig.DEPLOY_PARSER_USAGE+\
                     ScpDeploymentConfig.DEPLOY_PARSER_USAGE

    @classmethod
    def validate_configs(cls, args):
        try:
            if args.d == 'qubole':
                return QuboleDeploymentConfig.validate_configs(args)
            if args.d == 'remote':
                return ScpDeploymentConfig.validate_configs(args)
        except Exception as e:
            raise AfctlDeploymentException(e)


    @classmethod
    def deploy_project(cls, args, project_name, project_path):
        try:

            if args.type == "local":
                DockerDeploymentConfig.generate_dirs(project_path, project_name)
                return DockerDeploymentConfig.deploy_project(args, project_name)

            if args.type == "qubole":
                return QuboleDeploymentConfig.deploy_project(args, project_name)

            if args.type == "remote":
                return ScpDeploymentConfig.deploy_project(args, project_name)

        except Exception as e:
            raise AfctlDeploymentException(e)

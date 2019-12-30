from afctl.plugins.deployments.qubole.deployment_config import QuboleDeploymentConfig
from afctl.exceptions import AfctlDeploymentException

class DeploymentConfig():
    # Just append configs for other deployments here.
    CONFIG_DETAILS = QuboleDeploymentConfig.PARSER_USAGE

    @classmethod
    def validate_configs(cls, args):
        try:

            if args.d == 'qubole':
                return QuboleDeploymentConfig.validate_configs(args)


        except Exception as e:
            raise AfctlDeploymentException(e)
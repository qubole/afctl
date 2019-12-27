from afctl.plugins.deployments.base_deployment_config import BaseDeploymentConfig

# YAML structure
# deployment:
#   qubole:
#     name:
#       env:
#       cluster:
#       token:

class QuboleDeploymentConfig(BaseDeploymentConfig):
    PARSER_USAGE = \
    '            [ Qubole ]\n'+\
    '               -n : name of connection\n'+\
    '               -e : name of environment\n'+\
    '               -c : cluster label\n'+\
    '               -t : auth token\n'

    @classmethod
    def validate_configs(cls, args):
        config = {}
        if args.n is None:
            return config, True, "Name of connection is required to update config for Qubole."

        if args.e is not None:
            config['env'] = args.e

        if args.c is not None:
            config['cluster'] = args.c

        if args.t is not None:
            config['token'] = args.t

        import pdb; pdb.set_trace()
        return {'deployment':{'qubole':{args.n:config}}}, False, ""
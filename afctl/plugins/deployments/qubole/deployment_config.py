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

        if args.i:
            config['name'] = input("Enter name of connection : ")
            config['env'] = input("Enter environment : ")
            config['cluster'] = input("Enter cluster label : ")
            config['token'] = input("Enter auth token : ")

            return {'deployment':{'qubole':{config['name']:config}}}, False, ""
        else:
            if  args.n is None:
                return config, True, "Name of connection is required. Check usage."

            if args.e is not None:
                config['env'] = args.e

            if args.c is not None:
                config['cluster'] = args.c

            if args.t is not None:
                config['token'] = args.t

            if args.type == 'add' and (args.e is None or args.c is None or args.t is None):
                return {}, True, "All flags are required to add a new config. Check usage."

            return {'deployment':{'qubole':{args.n:config}}}, False, ""
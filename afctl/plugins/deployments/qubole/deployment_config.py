from afctl.plugins.deployments.base_deployment_config import BaseDeploymentConfig

# YAML structure
# deployment:
#   qubole:
#     name:
#       env:
#       cluster:
#       token:

class QuboleDeploymentConfig(BaseDeploymentConfig):

    # This is required to be displayed on the usage command. Please add the same to your deployment file.
    PARSER_USAGE = \
    '            [ Qubole ]\n'+\
    '               -n : name of connection\n'+\
    '               -e : name of environment\n'+\
    '               -c : cluster label\n'+\
    '               -t : auth token\n'

    @classmethod
    def validate_configs(cls, args):
        config = {}

        # No argument is provided. So we will ask for the input from the user.
        if args.e is None and args.c is None and args.t is None:

            # User could have provided the name of the connection.
            name = input("Enter name of connection : ") if args.n is None else args.n
            config['env'] = input("Enter environment : ")
            config['cluster'] = input("Enter cluster label : ")
            config['token'] = input("Enter auth token : ")

            # If update return the entire path because we are not sure if he has updated everything or only some values.
            if args.type == 'update':
                return {'deployment':{'qubole':{name:config}}}, False, ""

            # In add just append this to your parent.
            if args.type == 'add':
                return {name:config}, False, ""

        # Some arguments are given by the user. So don't ask for input.
        else:

            # Name of connection is compulsory in this flow.
            if  args.n is None:
                return config, True, "Name of connection is required. Check usage."

            if args.e is not None:
                config['env'] = args.e

            if args.c is not None:
                config['cluster'] = args.c

            if args.t is not None:
                config['token'] = args.t

            # For adding a new connection you need to provide all the configs.
            if args.type == 'add' and (args.e is None or args.c is None or args.t is None):
                return {}, True, "All flags are required to add a new config. Check usage."

            if args.type == 'update':
                return {'deployment':{'qubole':{args.n:config}}}, False, ""
            if args.type == "add":
                return {args.n:config}, False, ""

        return {}, False, "Some error has occurred."
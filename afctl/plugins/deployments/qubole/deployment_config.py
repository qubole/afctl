from afctl.plugins.deployments.base_deployment_config import BaseDeploymentConfig
from afctl.exceptions import AfctlDeploymentException
from afctl.plugins.deployments.qubole.qubole_utils import QuboleUtils
import yaml
from afctl.utils import Utility
import subprocess

# YAML structure
# deployment:
#   qubole:
#     name:
#       env:
#       cluster:
#       token:

class QuboleDeploymentConfig(BaseDeploymentConfig):

    # This is required to be displayed on the usage command. Please add the same to your deployment file.
    CONFIG_PARSER_USAGE = \
    '            [ Qubole ]\n'+\
    '               -n : name of deployment\n'+\
    '               -e : name of environment\n'+\
    '               -c : cluster label\n'+\
    '               -t : auth token\n'

    DEPLOY_PARSER_USAGE = \
    '   [qubole] - Deploy your project to QDS.\n'+\
    '       Arguments:\n'+\
    '           -n : Name of the deployment\n'

    @classmethod
    def generate_dirs(cls, main_dir, project_name):
        pass

    @classmethod
    def validate_configs(cls, args):
        try:
            config = {}
            # No argument is provided. So we will ask for the input from the user.
            if args.e is None and args.c is None and args.t is None:
                # User could have provided the name of the connection.
                name = input("Enter name of deployment : ") if args.n is None else args.n
                config['env'] = input("Enter environment : ")
                config['cluster'] = input("Enter cluster label : ")
                config['token'] = input("Enter auth token : ")

                config, flag, msg = QuboleUtils.sanitize_configs(config, args.type, name)
                if flag:
                    return {}, True, msg

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
                    return config, True, "Name of deployment is required. Check usage."

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

        except Exception as e:
            raise AfctlDeploymentException(e)


    @classmethod
    def deploy_project(cls, args, config_file):
        try:

            if args.n is None:
                return True, "-n is required. Check usage."

            with open(Utility.project_config(config_file)) as file:
                config = yaml.full_load(file)

            project = config_file
            origin = config['global']['git']['origin']
            token = config['global']['git']['access-token']

            if origin is None or origin == '':
                return True, "Origin is not set for the project. Run 'afctl config global -o <origin>'"

            params = QuboleUtils.generate_configs(config, args)
            latest_commit_on_remote = QuboleUtils.fetch_latest_commit(origin, params['branch'])

            if token is None or token == '':
                print("No personal access token found. The repository should be public.")

            if latest_commit_on_remote is None:
                return True, "Unable to read latest commit on origin. Please make sure the current branch is present on origin."

            print("Latest commit of {} on origin {} found.".format(params['branch'], origin))
            print("Deploying commit : {} on Qubole".format(latest_commit_on_remote))

            if token is not None and token != "":
                origin = QuboleUtils.create_private_repo_url(origin, token)

            qds_command = QuboleUtils.get_git_command(project, origin, params['branch'], latest_commit_on_remote)
            command = QuboleUtils.run_qds_command(params['env'], params['cluster'], params['token'], qds_command)
            if command.status != 'done':
                return True, "Deployment failed on Qubole"

            return False, ""

        except Exception as e:
            raise AfctlDeploymentException(e)
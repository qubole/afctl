from afctl.plugins.deployments.base_deployment_config import BaseDeploymentConfig
from afctl.exceptions import AfctlDeploymentException
import os
import yaml
from afctl.utils import Utility
import getpass
import paramiko
import scp

SEP = os.path.sep

# Yaml Structure
#   deployment:
#       remote:
#           host:
#           dagdir:
#           username:
#           password:
#           identity:

def unixify_path(p):
    """ target path MUST be Unix - cos airflow doesn't run on Windoz """
    return p.replace(SEP, '/')

class ScpDeploymentConfig(BaseDeploymentConfig):
    CONFIG_PARSER_USAGE = \
        '            [ remote ]\n' +\
        '               -m : airflow hostname\n' +\
        '               -c : airflow DAG directory\n' +\
        '               -u : login user (defaults to current user) \n' +\
        '               -e : login password\n' +\
        '               -i : identity file path (RSA private key)' +\
        '               You should have one of -p or -i.\n'

    DEPLOY_PARSER_USAGE = \
        '   [remote] - Deploy your project to remote Airflow instance.\n'


    @classmethod
    def validate_configs(cls, args):
        try:
            config = {}
            # No argument is provided. So we will ask for the input from the user.
            if args.m is None and args.c is None:
                config['host'] = input("Enter Airflow host : ")
                config['dagdir'] = input("Enter Airflow DAG dir : ")
                username = input("Enter remote username (empty if current): ")
                if username:
                    config['username'] = username
                password = input("Enter remote password (empty if identity file): ")
                if password:
                    config['password'] = password
                identity = input("Enter remote identity - RSA private key (empty if password) : ")
                if identity:
                    config['identity'] = identity
            
                # If update return the entire path because we are not sure if he has updated everything or only some values.
                if args.type == 'update':
                    return {'deployment':{'remote': config}}, False, ""

                # In add just append this to your parent.
                if args.type == 'add':
                    return {'remote': config}, False, ""

            # Some arguments are given by the user. So don't ask for input.
            else:

                # Name of connection is compulsory in this flow.
                if args.m is None:
                    return config, True, "Airflow host/IP required. Check usage."
 
                if args.c is None:
                    return config, True, "Airflow DAG directory required. Check usage."

                config['host'] = args.m
                config['dagdir'] = args.c
                
                if args.u is not None:
                    config['username'] = args.u

                if args.e is not None:
                    config['password'] = args.e

                if args.i is not None:
                    config['identity'] = args.i

                # For adding a new connection you need to provide at least these configs
                if args.type == 'add' and (args.m is None or args.c is None):
                    return {}, True, "Arguments are required to add a new config. Check usage."

                if args.type == 'update':
                    return {'deployment':{'remote': config}}, False, ""
                if args.type == "add":
                    return {'remote': config}, False, ""

            return {}, False, "Some error has occurred."

        except Exception as e:
            raise AfctlDeploymentException(e)

    @classmethod
    def generate_dirs(cls, main_dir):
        pass
    
    @classmethod
    def deploy_project(cls, args, config_file):
        try:
            project, project_path = Utility.find_project(os.getcwd())
        except TypeError:
            # hmmm - it returned None
            print("No project found!")
            return
             
        dags = []

        try:
            print("Deploying afctl project (%s) to remote" % project)

            with open(Utility.project_config(config_file)) as file:
                config = yaml.full_load(file)
                remote_dagdir = os.path.join(config['deployment']['remote']['dagdir'])
                for root, dirs, files in os.walk(project_path, topdown=True, followlinks=False):
                    # TODO - assure it's proper directory/file hierarchy
                    if root.find('%sdags%s' % (SEP,SEP)) != -1:
                        for dagname in files:
                            if dagname.endswith('.py'):
                                dags.append((os.path.join(root, dagname),
                                             unixify_path(os.path.join(remote_dagdir, dagname))))
 
            if dags is []:
                print("%s: no DAGs to ship" % project)
                return
            
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.load_system_host_keys()

            args = {
                'hostname': config['deployment']['remote']['host'],
                'username': config['deployment']['remote'].get('username', getpass.getuser()),
            }
            # look for user/password; otherwise go with ssh keys
            # TODO - maybe just a 'connect' label in the yaml; and pass exactly that as paramiko args ...
            if config['deployment']['remote'].get('password', None) is None:
                pkey_path = config['deployment']['remote'].get('identity',
                                                               os.path.join(os.path.expanduser("~"), '.ssh', 'id_rsa'))
                try:
                    args['pkey'] = paramiko.RSAKey.from_private_key_file(pkey_path)
                except FileNotFoundError:
                    raise FileNotFoundError('identity file missing: %s' % pkey_path)
                except paramiko.ssh_exception.SSHException as e:
                    raise paramiko.ssh_exception.SSHException('identity file invalid: %s\n%s' % (pkey_path, str(e)))
                #args['key_filename'] = pkey_path
            else:
                args['password'] = config['deployment']['remote']['password']
            try:
                ssh_client.connect(**args)
            except paramiko.BadHostKeyException as e:
                raise
            except paramiko.ssh_exception.AuthenticationException:
                if args.get('password', None) is not None:
                    args['password'] = '*******'
                raise paramiko.ssh_exception.AuthenticationException('Authentication Failure: %s' % args)
            
            with scp.SCPClient(ssh_client.get_transport()) as scp_client:
                for local_file, remote_file in dags:
                    scp_client.put(local_file, remote_file)
                scp_client.close() 
            
            ssh_client.close()

            return False, ""

        except Exception as e:
            raise AfctlDeploymentException(e)


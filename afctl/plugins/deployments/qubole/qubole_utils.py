import subprocess
from afctl.exceptions import AfctlDeploymentException
from mako.template import Template
from qds_sdk.qubole import Qubole
from qds_sdk.commands import ShellCommand
from urllib.parse import urlparse

class QuboleUtils():

    @staticmethod
    def fetch_latest_commit(origin, branch):
        try:
            commit = subprocess.run(['git', 'ls-remote', origin, 'refs/heads/{}'.format(branch), '|', 'cut', '-f', '1'], stdout=subprocess.PIPE)
            commit = commit.stdout.decode('utf-8')

            if commit == '':
                return None

            return commit.split('\t')[0]

        except Exception as e:
            raise AfctlDeploymentException(e)


    @staticmethod
    def get_git_command(project, origin, branch, latest_commit_on_remote):
        template = Template(
            """
cd /tmp
mkdir qubole_${latest_commit_on_remote}
cd qubole_${latest_commit_on_remote}
git clone --single-branch -b ${branch} ${origin}
cd ${project}
source /etc/profile.d/airflow.sh
if [[ -d $AIRFLOW_HOME/dags/${project} ]]; then
rm -rf $AIRFLOW_HOME/dags/${project}
fi
yes | cp -rf ${project} $AIRFLOW_HOME/dags/
if [[ -d $AIRFLOW_HOME/plugins/${project} ]]; then
rm -rf $AIRFLOW_HOME/plugins/${project}
fi
mkdir $AIRFLOW_HOME/plugins/${project}
yes | cp -rf plugins $AIRFLOW_HOME/plugins/${project}
rm -rf /tmp/qubole_${latest_commit_on_remote}
cd $AIRFLOW_HOME
sudo monit restart webserver
sudo monit restart scheduler"""
        )

        return template.render_unicode(
            latest_commit_on_remote = latest_commit_on_remote,
            branch = branch,
            origin = origin,
            project = project
        )

    @staticmethod
    def run_qds_command(env, cluster, token, qds_command):
        try:
            Qubole.configure(api_token = token, api_url = env)
            shell_cmd = ShellCommand.run(inline=qds_command, label=cluster)
            return shell_cmd

        except Exception as e:
            raise AfctlDeploymentException(e)

    @staticmethod
    def sanitize_configs(config, type, name):
        try:
            new_conf = {}
            if name == "":
                return {}, True, "Name cannot be blank"

            if type == "add":
                for k, v in config.items():
                    if v == "":
                        return {}, True, "All arguments are mandatory."
                new_conf = config

            if type == "update":
                for k, v in config.items():
                    if v != "":
                        new_conf[k] = v

            return new_conf, False, ""
        except Exception as e:
            raise AfctlDeploymentException(e)

    @staticmethod
    def generate_configs(configs, args):
        try:
            name = args.n
            config = configs['deployment']['qubole'][name]
            env = "{}/api".format(config['env'].rstrip('/'))
            cluster = config['cluster']
            token = config['token']
            branch = subprocess.run(['git', 'symbolic-ref', '--short', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]

            return{
                'name': name,
                'env': env,
                'cluster': cluster,
                'token': token,
                'branch': branch
            }
        except Exception as e:
            raise AfctlDeploymentException(e)

    @staticmethod
    def create_private_repo_url(origin, token):
        try:
            url = urlparse(origin)
            org = url.path.split('/')[1]
            url = "https://{}:{}@github.com{}".format(org, token, url.path)
            return url
        except Exception as e:
            raise AfctlDeploymentException(e)
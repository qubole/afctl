import subprocess
from afctl.exceptions import AfctlDeploymentException
from mako.template import Template
from qds_sdk.qubole import Qubole
from qds_sdk.commands import ShellCommand

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
yes | cp -rf ${project} $AIRFLOW_HOME/dags/
rm -rf /tmp/qubole_${latest_commit_on_remote}"""
        )

        return template.render_unicode(
            latest_commit_on_remote = latest_commit_on_remote,
            branch = branch,
            origin = origin,
            project = project
        )

    @staticmethod
    def run_qds_command(env, cluster, token, qds_command):
        Qubole.configure(api_token = token, api_url = env)
        shell_cmd = ShellCommand.run(inline=qds_command, label=cluster)
        return shell_cmd

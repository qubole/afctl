import subprocess
from afctl.exceptions import AfctlDeploymentException

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

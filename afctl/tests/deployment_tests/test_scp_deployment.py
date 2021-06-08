from afctl.plugins.deployments.scp.deployment_config import ScpDeploymentConfig
from afctl.tests.utils import clean_up, PROJECT_NAME
import pytest
import os, pathlib, tempfile
import paramiko

TMP = tempfile.gettempdir()
PROJECT_CONFIG_DIR=os.path.join(TMP, PROJECT_NAME, '.afctl_config')
PROJECT_CONFIG_FILE="{}.yml".format(os.path.join(PROJECT_CONFIG_DIR, PROJECT_NAME))
HOME = os.path.expanduser('~')


class DummyArgParse:

    def __init__(self, type=None, host=None, dagdir=None, username=None, password=None, identity=None):
        self.type = type
        self.m = host
        self.c = dagdir
        self.u = username
        self.e = password
        self.i = identity


class TestSCPDeployment:

    @pytest.fixture(scope='function')
    def create_project(self):
        main_dir = os.path.join(TMP, PROJECT_NAME)
        clean_up(main_dir)
        os.makedirs(main_dir, exist_ok=True)
        os.makedirs(PROJECT_CONFIG_DIR, exist_ok=True)
        os.makedirs(os.path.join(main_dir, 'deployments'), exist_ok=True)
        os.makedirs(os.path.join(main_dir, 'dags'), exist_ok=True)
        public_keypath = os.path.join(HOME, '.ssh', 'id_rsa.pub')
        private_keypath = os.path.join(HOME, '.ssh', 'id_rsa')
        config_file_content = """---
global:
    airflow_version:
    git:
        origin:
        access-token:
deployment:
    qubole:
    local:
        compose:
    remote:
        host: localhost
        dagdir: %s
        username: %s
        password: %s
""" % (os.path.join(main_dir, 'dags'), public_keypath, private_keypath)

        with open(PROJECT_CONFIG_FILE, 'w') as file:
            file.write(config_file_content)

        #key = paramiko.RSAKey.generate(1024)
        #key.write_private_key_file(private_keypath)
   
        #with open(public_keypath, "w") as public:
        #    public.write("%s %s"  % (key.get_name(), key.get_base64()))
        #public.close()
            
        yield main_dir
        #clean_up(main_dir)

    def test_scp(self, create_project):
        # wtf - Utility.project_config() futzes with path suffix ...
        ScpDeploymentConfig.deploy_project({}, PROJECT_CONFIG_FILE.replace('.yml',''))

    def test_validate_configs_on_add_pass(self):
        args = DummyArgParse(type='add', host='localhost', dagdir='/var/lib/airflow/dags')
        val = ScpDeploymentConfig.validate_configs(args)
        assert val[0] == {'remote': {'host': 'localhost', 'dagdir': '/var/lib/airflow/dags'}}
        assert val[1] is False
        assert val[2] == ''

    def test_validate_configs_on_add_fail(self):
        args = DummyArgParse(type='add', host='localhost')
        val = ScpDeploymentConfig.validate_configs(args)
        assert val[0] == {}
        assert val[1] is True
        assert val[2] == 'Airflow DAG directory required. Check usage.'

    def test_validate_configs_on_update_pass(self):
        args = DummyArgParse(type='update', host='localhost', dagdir='/var/lib/airflow/dags')
        val = ScpDeploymentConfig.validate_configs(args)
        assert val[0] == {'deployment':
                          {'remote': {'host': 'localhost',
                                      'dagdir': '/var/lib/airflow/dags'}}}
        assert val[1] is False
        assert val[2] == ''

    def test_validate_configs_on_update_fail(self):
        args = DummyArgParse(type='update', host='localhost')
        val = ScpDeploymentConfig.validate_configs(args)
        assert val[0] == {}
        assert val[1] is True
        assert val[2] == 'Airflow DAG directory required. Check usage.'


import pytest
from afctl.tests.utils import *
from afctl.plugins.deployments.qubole.deployment_config import QuboleDeploymentConfig
from afctl.plugins.deployments.qubole.qubole_utils import QuboleUtils



class TestQuboleDeployment:

    # validate configs
    def test_validate_configs_on_add_should_pass(self):
        args = DummyArgParse(type='add', env='test_env', cluster='test_cluster', token='test_token', name="test_name")
        val = QuboleDeploymentConfig.validate_configs(args)
        assert str(val[0]) == "{'test_name': {'env': 'test_env', 'cluster': 'test_cluster', 'token': 'test_token'}}"
        assert val[1] is False
        assert val[2] is ''

    def test_validate_configs_on_add_should_fail_1(self):
        args = DummyArgParse(type='add', env='test_env', cluster='test_cluster', token='test_token')
        val = QuboleDeploymentConfig.validate_configs(args)
        assert val[1] is True
        assert val[2] == "Name of deployment is required. Check usage."

    def test_validate_configs_on_add_should_fail_2(self):
        args = DummyArgParse(type='add', env='test_env', cluster='test_cluster', name="test_name")
        val = QuboleDeploymentConfig.validate_configs(args)
        assert val[1] is True
        assert val[2] == "All arguments are required to add a new config. Check usage."


    def test_validate_configs_on_update_should_pass_1(self):
        args = DummyArgParse(type='update', env='test_env', cluster='test_cluster', token='test_token', name="test_name")
        val = QuboleDeploymentConfig.validate_configs(args)
        assert str(val[0]) == "{'deployment': {'qubole': {'test_name': {'env': 'test_env', 'cluster': 'test_cluster', 'token': 'test_token'}}}}"
        assert val[1] is False
        assert val[2] is ''

    def test_validate_configs_on_update_should_pass_2(self):
        args = DummyArgParse(type='update', env='test_env', token='test_token', name="test_name")
        val = QuboleDeploymentConfig.validate_configs(args)
        assert str(val[0]) == "{'deployment': {'qubole': {'test_name': {'env': 'test_env', 'token': 'test_token'}}}}"
        assert val[1] is False
        assert val[2] is ''

    def test_sansitize_config_on_add_1(self):
        config = {
            'env': 'test_env',
            'cluster' : 'test_cluster',
            'token': 'new_token'
        }
        val = QuboleUtils.sanitize_configs(config, "add", "")
        assert val[1] is True
        assert val[2] == "Name cannot be blank."

    def test_sansitize_config_on_add_2(self):
        config = {
            'env': 'test_env',
            'cluster' : 'test_cluster',
            'token': ''
        }
        val = QuboleUtils.sanitize_configs(config, "add", "test_name")
        assert val[1] is True
        assert val[2] == "All arguments are mandatory."

    def test_sansitize_config_on_add_3(self):
        config = {
            'env': 'test_env',
            'cluster' : 'test_cluster',
            'token': 'new_token'
        }
        val = QuboleUtils.sanitize_configs(config, "add", "test_name")
        assert str(val[0]) == "{'env': 'test_env', 'cluster': 'test_cluster', 'token': 'new_token'}"
        assert val[1] is False
        assert val[2] is ""

    def test_sansitize_config_on_update_1(self):
        config = {
            'env': 'test_env',
            'cluster' : 'test_cluster',
            'token': 'new_token'
        }
        val = QuboleUtils.sanitize_configs(config, "update", "test_name")
        assert str(val[0]) == "{'env': 'test_env', 'cluster': 'test_cluster', 'token': 'new_token'}"
        assert val[1] is False
        assert val[2] is ""

    def test_sansitize_config_on_update_2(self):
        config = {
            'env': 'test_env',
            'cluster' : '',
            'token': 'new_token'
        }
        val = QuboleUtils.sanitize_configs(config, "update", "test_name")
        assert str(val[0]) == "{'env': 'test_env', 'token': 'new_token'}"
        assert val[1] is False
        assert val[2] is ""

    def test_create_private_repo_url(self):
        origin = "https://github.com/test_origin"
        token = "test_token"
        url = QuboleUtils.create_private_repo_url(origin, token)
        assert url == 'https://test_origin:test_token@github.com/test_origin'


    def test_get_shell_command(self):
        project = "test_project"
        origin = "test_origin"
        branch = "test_brancg"
        latest_commit_on_remote = "test_commit"
        expected_cmd = '\ncd /tmp\nmkdir qubole_test_commit\ncd qubole_test_commit\ngit clone --single-branch -b test_brancg test_origin\ncd test_project\nsource /etc/profile.d/airflow.sh\nif [[ -d $AIRFLOW_HOME/dags/test_project ]]; then\nrm -rf $AIRFLOW_HOME/dags/test_project\nfi\nyes | cp -rf test_project $AIRFLOW_HOME/dags/\nif [[ -d $AIRFLOW_HOME/plugins/test_project ]]; then\nrm -rf $AIRFLOW_HOME/plugins/test_project\nfi\nmkdir $AIRFLOW_HOME/plugins/test_project\nyes | cp -rf plugins $AIRFLOW_HOME/plugins/test_project\nrm -rf /tmp/qubole_test_commit\ncd $AIRFLOW_HOME\nsudo monit restart webserver\nsudo monit restart scheduler'
        cmd = QuboleUtils.get_shell_command(project, origin, branch, latest_commit_on_remote)
        assert cmd == expected_cmd
from afctl.plugins.deployments.docker.deployment_config import DockerDeploymentConfig
from afctl.tests.utils import clean_up, PROJECT_NAME, PROJECT_CONFIG_DIR
import pytest
import os, pathlib, tempfile

TMP = tempfile.gettempdir()


class TestLocalDeployment:

    @pytest.fixture(scope='function')
    def create_project(self):
        clean_up(PROJECT_NAME)
        clean_up(PROJECT_CONFIG_DIR)
        main_dir = os.path.join(TMP, PROJECT_NAME)
        os.makedirs(main_dir, exist_ok=True)
        os.makedirs(PROJECT_CONFIG_DIR, exist_ok=True)
        os.makedirs(os.path.join(main_dir, 'deployments'), exist_ok=True)
        config_file = "{}.yml".format(os.path.join(PROJECT_CONFIG_DIR, PROJECT_NAME))
        pathlib.Path(config_file).touch()
        config_file_content = """
global:
    airflow_version:
    git:
        origin:
        access-token:
deployment:
    qubole:
    local:
        compose:
        """
        with open(config_file, 'w') as file:
            file.write(config_file_content)

        yield main_dir
        clean_up(PROJECT_NAME)
        clean_up(PROJECT_CONFIG_DIR)

    def test_docker_compose_generation(self, create_project):
        DockerDeploymentConfig.generate_dirs(create_project, PROJECT_NAME)
        config_file = "{}.yml".format(os.path.join(PROJECT_CONFIG_DIR, PROJECT_NAME))
        expected_output = """global:
    airflow_version: null
    git:
        origin: null
        access-token: null
deployment:
    qubole: null
    local:
        compose: /tmp/test_project/deployments/test_project-docker-compose.yml
        """

        current_output = open(config_file).read()
        expected_output = expected_output.replace(" ", "")
        current_output = current_output.replace(" ", "")
        assert expected_output == current_output

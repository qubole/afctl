from afctl.parsers import Parser
import pytest
import os
from afctl.tests.utils import clean_up, check_paths, PROJECT_NAME, PROJECT_CONFIG_DIR, DummyArgParse

class TestParser:

    @pytest.fixture(scope='module')
    def create_parser(self):
        clean_up(PROJECT_NAME, PROJECT_CONFIG_DIR)
        parser = Parser.setup_parser()
        yield parser
        clean_up(PROJECT_NAME, PROJECT_CONFIG_DIR)


    def test_init(self, create_parser):
        func = 'init'
        args = create_parser.parse_args([func, PROJECT_NAME])
        args.func(args)
        assert os.path.exists(PROJECT_NAME) is True
        sub_files = ['.afctl_project', '.gitignore', 'requirements.txt']
        sub_dirs = [PROJECT_NAME, 'deployments', 'migrations', 'plugins', 'tests']
        project_dirs = ['dags', 'commons']

        # Positive test cases.
        assert check_paths([PROJECT_NAME], sub_files) is True
        assert check_paths([PROJECT_NAME], sub_dirs) is True
        assert check_paths([os.path.join(PROJECT_NAME,PROJECT_NAME)], project_dirs) is True

        # Negative test cases.
        assert check_paths([PROJECT_NAME], ['dummy']) is False


    def test_configs(self, create_parser):
        args = DummyArgParse(type="global", origin="new_origin", token="new_token", version="1.10.0")
        Parser.act_on_configs(args, PROJECT_NAME)
        config_file = "{}.yml".format(os.path.join(PROJECT_CONFIG_DIR, PROJECT_NAME))
        expected_output = """global:
    airflow_version: 1.10.0
    git:
        origin: new_origin
        access-token: new_token
deployment:
    qubole: null
    local:
        compose: null
        """
        current_output = open(config_file).read()
        expected_output = expected_output.replace(" ", "")
        current_output = current_output.replace(" ", "")
        assert expected_output == current_output

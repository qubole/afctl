from afctl.parsers import Parser
import pytest
import os
from afctl.tests.parser_tests.parser_utils import clean_up, check_paths

class TestParser:

    PROJECT_NAME = 'test_project'
    PROJECT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), '.afctl_config')



    @pytest.fixture(scope='session')
    def create_parser(self):
        clean_up(self.PROJECT_NAME, self.PROJECT_CONFIG_DIR)
        parser = Parser.setup_parser()
        yield parser
        clean_up(self.PROJECT_NAME, self.PROJECT_CONFIG_DIR)


    def test_init(self, create_parser):
        func = 'init'
        args = create_parser.parse_args([func, self.PROJECT_NAME])
        args.func(args)
        assert os.path.exists(self.PROJECT_NAME) is True
        sub_files = ['.afctl_project', '.gitignore', 'requirements.txt']
        sub_dirs = [self.PROJECT_NAME, 'deployments', 'migrations', 'plugins', 'tests']
        project_dirs = ['dags', 'commons']

        # Positive test cases.
        assert check_paths([self.PROJECT_NAME], sub_files) is True
        assert check_paths([self.PROJECT_NAME], sub_dirs) is True
        assert check_paths([os.path.join(self.PROJECT_NAME,self.PROJECT_NAME)], project_dirs) is True

        # Negative test cases.
        assert check_paths([self.PROJECT_NAME], ['dummy']) is False


    def test_init_2(self):
        func = 'init'

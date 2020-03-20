from afctl.utils import Utility
import pytest
import os, subprocess
from afctl.tests.utils import create_path_and_clean, PROJECT_NAME, PROJECT_CONFIG_DIR, clean_up

class TestUtils:

    @pytest.fixture(scope='function')
    def clean_tmp_dir(self):
        parent = ['/tmp']
        child = ['one', 'two', 'three']
        create_path_and_clean(parent, child)
        yield
        create_path_and_clean(parent, child)

    # create_dirs
    def test_create_dir(self, clean_tmp_dir):
        parent = ['/tmp']
        child = ['one', 'two', 'three']
        dirs = Utility.create_dirs(parent, child)
        assert dirs['one'] == '/tmp/one'
        assert os.path.exists(dirs['one']) is True
        assert dirs['two'] == '/tmp/two'
        assert os.path.exists(dirs['two']) is True
        assert dirs['three'] == '/tmp/three'
        assert os.path.exists(dirs['three']) is True

    # create_files
    def test_create_files(self, clean_tmp_dir):
        parent = ['/tmp']
        child = ['one', 'two', 'three']
        dirs = Utility.create_files(parent, child)
        assert dirs['one'] == '/tmp/one'
        assert os.path.exists(dirs['one']) is True
        assert dirs['two'] == '/tmp/two'
        assert os.path.exists(dirs['two']) is True
        assert dirs['three'] == '/tmp/three'
        assert os.path.exists(dirs['three']) is True

    # project_config
    def test_return_project_config_file(self):
        project = "test_project"
        expected_path = os.path.join(PROJECT_CONFIG_DIR, project)+".yml"
        path = Utility.project_config(project)
        assert path == expected_path

    # generate_dag_template
    def test_generate_dag_template(self):
        project_name = "tes_project"
        path = "/tmp"
        dag = "test"
        Utility.generate_dag_template(project_name, dag, path)
        expected_output = """ 
from airflow import DAG
from datetime import datetime, timedelta

default_args = {
'owner': 'tes_project',
# 'depends_on_past': ,
# 'start_date': ,
# 'email': ,
# 'email_on_failure': ,
# 'email_on_retry': ,
# 'retries': 0

}

dag = DAG(dag_id='test', default_args=default_args, schedule_interval='@once')


        """
        current_output = open(os.path.join('/tmp', 'test_dag.py')).read()
        expected_output = expected_output.replace(" ", "")
        current_output = current_output.replace(" ", "")
        assert expected_output == current_output

    @pytest.fixture(scope='function')
    def create_project(self):
        path = '/tmp/one/two/three'
        subprocess.run(['mkdir', '-p', path])
        file_path = '/tmp/one/two/.afctl_project'
        subprocess.run(['touch', file_path])
        yield
        subprocess.run(['rm', '-rf', path])

    # find_project
    def test_find_project(self, create_project):
        path = '/tmp/one/two/three'
        project = Utility.find_project(path)
        assert project[0] == 'two'
        assert project[1] == '/tmp/one/two'


    @pytest.fixture(scope='function')
    def create_config_file(self):
        subprocess.run(['mkdir', PROJECT_CONFIG_DIR])
        file_path = os.path.join(PROJECT_CONFIG_DIR, PROJECT_NAME)+'.yml'
        subprocess.run(['touch', file_path])
        yml_template = """
parent:
    child1:
    child2:
        """

        with open(file_path, 'w') as file:
            file.write(yml_template)
        yield
        clean_up(PROJECT_CONFIG_DIR)

    # add_configs update_config
    def test_add_and_update_configs(self, create_config_file):
        add_config = {'name': {'key1': 'val1', 'key2': 'val2'}}
        Utility.add_configs(['parent', 'child1'], PROJECT_NAME, add_config)
        config_file = os.path.join(PROJECT_CONFIG_DIR, PROJECT_NAME)+'.yml'

        expected_output = """parent:
    child1:
        name:
            key1: val1
            key2: val2
    child2: null
        """

        current_output = open(config_file).read()
        expected_output = expected_output.replace(" ", "")
        current_output = current_output.replace(" ", "")
        assert expected_output == current_output

        add_config = {'name': {'key3': 'val3', 'key4': 'val4'}}
        Utility.add_configs(['parent', 'child2'], PROJECT_NAME, add_config)

        expected_output = """parent:
    child1:
        name:
            key1: val1
            key2: val2
    child2: 
        name:
            key3: val3
            key4: val4
        """
        current_output = open(config_file).read()
        expected_output = expected_output.replace(" ", "")
        current_output = current_output.replace(" ", "")
        assert expected_output == current_output


        update_config = {'parent': {'child2': {'name' : {'key3': 'val100'}}}}
        Utility.update_config(PROJECT_NAME, update_config)
        expected_output = """parent:
    child1:
        name:
            key1: val1
            key2: val2
    child2: 
        name:
            key3: val100
            key4: val4
        """
        current_output = open(config_file).read()
        expected_output = expected_output.replace(" ", "")
        current_output = current_output.replace(" ", "")
        assert expected_output == current_output
from afctl.utils import Utility
import pytest
import os, pathlib, shutil, tempfile
from afctl.tests.utils import create_path_and_clean, PROJECT_NAME, PROJECT_CONFIG_DIR, clean_up

SEP = os.path.sep
TMP = tempfile.gettempdir()
TMP_NO_SEP = TMP.replace(SEP,'')

class TestUtils:

    @pytest.fixture(scope='function')
    def clean_tmp_dir(self):
        parent = [TMP]
        child = ['one', 'two', 'three']
        create_path_and_clean(parent, child)
        yield
        create_path_and_clean(parent, child)

    # create_dirs
    def test_create_dir(self, clean_tmp_dir):
        parent = [TMP]
        child = ['one', 'two', 'three']
        dirs = Utility.create_dirs(parent, child)
        assert dirs['one'] == SEP.join([TMP, 'one'])
        assert os.path.isdir(dirs['one'])
        assert dirs['two'] == SEP.join([TMP, 'two'])
        assert os.path.isdir(dirs['two'])
        assert dirs['three'] == SEP.join([TMP, 'three'])
        assert os.path.isdir(dirs['three'])

    # create_files
    def test_create_files(self, clean_tmp_dir):
        parent = [TMP]
        child = ['one', 'two', 'three']
        dirs = Utility.create_files(parent, child)
        assert dirs['one'] == SEP.join([TMP, 'one'])
        assert os.path.exists(dirs['one']) is True
        assert dirs['two'] == SEP.join([TMP, 'two'])
        assert os.path.exists(dirs['two']) is True
        assert dirs['three'] == SEP.join([TMP, 'three'])
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
        path = TMP
        dag = "test"
        Utility.generate_dag_template(project_name, dag, path)
        expected_output = """ 
from airflow import DAG
from datetime import datetime, timedelta

default_args = {
'owner': 'tes_project',
'start_date': datetime.now() - timedelta(days=1),
# 'depends_on_past': ,
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
        path = os.path.sep.join([TMP, 'one', 'two', 'three'])
        os.makedirs(path, exist_ok=True)
        file_path = os.path.sep.join([TMP, 'one', 'two', '.afctl_project'])
        pathlib.Path(file_path).touch()
        yield
        shutil.rmtree(path)

    # find_project
    def test_find_project(self, create_project):
        path = os.path.sep.join([TMP, 'one', 'two', 'three'])
        project = Utility.find_project(path)
        assert project[0] == 'two'
        assert project[1] == os.path.sep.join([TMP, 'one', 'two'])


    @pytest.fixture(scope='function')
    def create_config_file(self):
        os.mkdir(PROJECT_CONFIG_DIR)
        file_path = os.path.join(PROJECT_CONFIG_DIR, PROJECT_NAME)+'.yml'
        pathlib.Path(file_path).touch()
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

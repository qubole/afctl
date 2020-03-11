from afctl.utils import Utility
import pytest
import os
from afctl.tests.utils import create_path_and_clean, PROJECT_CONFIG_DIR

class TestUtils:

    @pytest.fixture(scope='function')
    def clean_tmp_dir(self):
        parent = ['/tmp']
        child = ['one', 'two', 'three']
        create_path_and_clean(parent, child)
        yield
        create_path_and_clean(parent, child)

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

    def test_return_project_config_file(self):
        project = "test_project"
        expected_path = os.path.join(PROJECT_CONFIG_DIR, project)+".yml"
        path = Utility.project_config(project)
        assert path == expected_path


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


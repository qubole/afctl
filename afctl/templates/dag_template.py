from mako.template import Template

def dag_template(name):
    template = Template(
"""
from airflow import DAG
from datetime import datetime, timedelta

default_args = {
'owner': 'airflow',
# 'depends_on_past': ,
# 'start_date': ,
# 'email': ,
# 'email_on_failure': ,
# 'email_on_retry': ,
# 'retries': 0,
# schedule_interval=

}

dag = DAG(dag_id=${name}, default_args=default_args)

    
"""
    )

    return template.render_unicode(name=name)
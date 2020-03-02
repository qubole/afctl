# afctl

The proposed CLI tool is authored to make creating and deployment of airflow projects faster and smoother. 
As of now, there is no tool out there that can empower the user to create a boilerplate code structure for airflow 
projects and make development + deployment of projects seamless.

## Installation

Create a new python virtualenv. You can use the following command. <br />
```bash
python3 -m venv <name>
```
Activate your virtualenv<br/>
```bash
source /path_to_venv/bin/activate
```

```bash
pip3 install afctl
```
or<br/>

Clone this repository. <br />
Move into the repository and run <br/>
```bash
pip3 install .
```


## Requirements
* Python 3.5+
* Docker

## Usage

Commands right now supported are
* init
* config
* deploy
* list
* generate

To learn more, run 
```bash
afctl <command> -h
```
<br>

## Initialize a new afctl project. 
The project is created in your present working directory. Along with this a configuration file with the same name is 
generated in **/home/.afctl_configs** directory.


```bash
afctl init “name of the project”
```

* Creates a new project directory.
* Creates a config file in the home directory

If you already have a git repository and want to turn it into an afctl project.
Run the following command :-
```bash
afctl init .
```
* Initialize the current directory as a project
<br>

## Manage configurations

The configuration file is used for deployment contains the following information.
```yaml
global:
-airflow_version:
-git:
--origin:
--access-token:
deployment:
-qubole:
--local:
---compose:
```
<br>

* `airflow_version` can be added to the project when you initialize the project.
```bash
afctl init <name> -v <version>
```

* `global configs (airflow_version, origin, access-token)` can all be added/ updated with the following command :

```bash
afctl config global -o <git-origin> -t <access-token> -v <airflow_version>
``` 

## Deploy project locally
* Initialize a new afctl project
```bash
afctl init project_demo
```
* The following directory structure will be generated
```bash
.
├── deployments
│   └── project_demo-docker-compose.yml
├── migrations
├── plugins
├── project_demo
│   ├── commons
│   └── dags
├── requirements.txt
└── tests
```
You can add python packages that will be required by your dags in `requirements.txt`. They will automatically get
installed.
* Add a new module in the project.
```bash
afctl generate module -n <name of the module>
```

The following directory structure will be generated :

```bash
afctl generate module -n first_module
afctl generate module -n second_module

.
├── deployments
│   └── project_demo-docker-compose.yml
├── migrations
├── plugins
├── project_demo
│   ├── commons
│   └── dags
│       ├── first_module
│       └── second_module
├── requirements.txt
└── tests
    ├── first_module
    └── second_module

```

* You can generate dags using the following command :

```bash
afctl generate dag -n <name of dag> -m <name of module>
```

The following directory structure will be generate :

```bash
afctl generate dag -n new -m first_module

.
├── deployments
│   └── project_demo-docker-compose.yml
├── migrations
├── plugins
├── project_demo
│   ├── commons
│   └── dags
│       ├── first_module
│       │   └── new_dag.py
│       └── second_module
├── requirements.txt
└── tests
    ├── first_module
    └── second_module
```

The dag file will look like this :

```python
from airflow import DAG
from datetime import datetime, timedelta

default_args = {
'owner': 'project_demo',
# 'depends_on_past': ,
# 'start_date': ,
# 'email': ,
# 'email_on_failure': ,
# 'email_on_retry': ,
# 'retries': 0

}

dag = DAG(dag_id='new', default_args=default_args, schedule_interval='@once')
```

* To deploy your project, run the following command (make sure docker is running) :

```bash
afctl deploy local
```
If you do not want to see the logs, you can run 
```bash
afctl deploy local -d
```
This will run it in detached mode and won't print the logs on the console.

* You can access your airflow webserver on browser at `localhost:8080`

## Deploy project on Qubole

* Initialize a new project and add git-origin and access-token (if want to keep the project as private repo
on Github) to the configs.
* Push the project once completed to Github.
* Deploying to Qubole will require adding deployment configurations.
```bash
afctl config add -d qubole -n <name of deployment> -e <env> -c <cluster-label> -t <auth-token>
```
This command will modify your config file. You can see your config file with the following command :
```bash
afctl config show
```

For example - 
```bash
afctl config add -d qubole -n demo -e https://api.qubole.com -c airflow_1102 -t khd34djs3
```

* To deploy run the following command
```bash
afctl deploy qubole -n <name>
```

### Caution
Not yet ported for Windows.

#### Credits
Docker-compose file : https://github.com/puckel/docker-airflow 


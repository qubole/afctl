#afctl

The proposed CLI tool is being authored to make creating and deployment of airflow projects faster and smoother. 
As of now, there is no tool out there that can empower the user to create a boilerplate code structure for airflow 
projects and make development + deployment of projects seamless.

## Installation

Clone the repository. <br />
Create a new python virtualenv. You can use the following command. <br />
```bash
python3 -m venv <name>
```
Activate your virtualenv<br/>
```bash
source /path_to_venv/bin/activate
```

Step into the afctl directory and run <br/>
```bash
pip3 install .
```

## Requirements
Python 3.5+

##Usage

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

#### Initialize a new afctl project. 
The project is created in your present working directory. Along with this a configuration file with the same name is 
generated in **/home/afctl_configs** directory.


```bash
afctl init “name of the project”
```

* Creates a new project directory.
* Creates a config file in the home directory

```bash
afctl init .
```
* Initialize the current directory as a project
* If the directory is already a git repository then the global configs will get automatically set.
<br>

#### Manage configurations

The configuration file is used for deployment.
```yaml
global:
  git:
    origin:
deployment:
  qubole:
  docker-local:
    compose:
```
<br>

```
TYPES:
   add - add a config for your deployment.
   update - update an existing config for your deployment.
       Arguments:
           -d : Deployment Type
           -p : Project
            [ Qubole ]
               -n : name of connection
               -e : name of environment
               -c : cluster label
               -t : auth token
            [ docker-local ]
               Cannot add/update configs.
   global
       Arguments:
           -p : Project
           -o : Set git origin for deployment
   show -  Show the config file on console
       No arguments.

positional arguments:
  {add,update,show,global}

optional arguments:
  -h, --help            show this help message and exit
  -d {qubole}
  -o O
  -p P
  -n N
  -e E
  -c C
  -t T
```

```bash
afctl config global -o {origin}
```
* Will set the git origin for your project.
* Supports both inline arguments as well as promoting for input.

```bash
afctl configs add -d {deployment}
```
* Prompts the user to input connector related values.
*  Can also provide values as inline arguments.

```bash
afctl configs update -d {deployment}
```

* Prompts the user to update the values
* Can also provide inline arguments.

```bash
afctl deploy {deployment} -n {name of connection}
```
* Fetches the latest commit in remote origin.
* Deploys the repository with the last commit as shown.

```bash
afctl config show
```

* Prints the configuration file on the console.


### Caution
Not yet ported for Windows.


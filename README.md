<div align="center">    

# Services in Industry 4.0. Modeling and composition @ SummerSOC 2023

![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black)
![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
[![Sapienza](https://img.shields.io/badge/Sapienza_University_of_Rome-blue?style=flatlabelColor=781A2D&color=781A2D&logoColor=white)](https://www.diag.uniroma1.it/gruppi-di-ricerca/25462)
[![Licence](https://img.shields.io/github/license/Ileriayo/markdown-badges?style=flat)](./LICENSE)

</div>

AIDA (Adaptive InDustrial APIs) is a tool for the composition of Industrial APIs for resilience manufacturing. 

The proposed technique generates a plan for a manufacturing process by orchestrating manufacturing actors which are depicted as services.

## Architecture
<div align="center">    
<img width="80%" src="images/architecture_tutta.png">
</div>

- **Controller**: computing the plan
- **Enactor**: acting as a middleware between controller and Industrial API
- **Industrial API** platform: realizing the services representing the manufacturing actors


## Preliminaries

We assume the user uses a **UNIX-like** machine and that has **Python 3.10** installed.

- To set up the virtual environment install [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/) (<code>pip install pipenv</code>), then execute
```bash
pipenv install --dev
```

- Start a shell within the Python virtual environment (to be done whenever a new terminal is opened):
```bash
pipenv shell
```

- Install the Python package in development mode:
```bash
pip install -e .
```

- Install Graphviz to use rendering functionalities. 
  At [this page](https://www.graphviz.org/download/) you will find the releases for all the supported platform.

- Install [Lydia](https://github.com/whitemech/lydia). 
  We suggest to install it by [building it from source](https://github.com/whitemech/lydia#build-from-source).

- Install [Fast Downward](https://github.com/aibasel/downward) planner:
```bash
cd alto
git clone https://github.com/aibasel/downward.git
cd downward
./build.py
```

- Generate Python client from OpenAPI v3.0 specification (maybe you need to change permissions of the script file):
```bash
cd local/IndustrialAPI/actors_api_lmdp_ltlf/openapi_client_script
# chmod 777 generate-openapi-client.sh
./generate-openapi-client.sh

cd local/IndustrialAPI/actors_api_plan/openapi_client_script
# chmod 777 generate-openapi-client.sh
./generate-openapi-client.sh
```

## Run the tool
To run the tool you need to run the GUI script
```bash
cd GUI
python Adaptive.py
```

### Design time
A design time frame allows to model both services (.sdl) and manufacturing goal (.tdl). Such models are usually saved in specific folders inside [saved_models](GUI/saved_models/).

### Run time
<div align="center">    
<img width=80% src="images/runtime.png">
</div>

A run time frame allows to generate and execute the optimal policy (plan). The set-up of this phase depends on the selection of a proper configuration file. [config_files](GUI/config_files/) contains some configuration files.


## License
The software is released under the MIT license.

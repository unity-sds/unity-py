# Unity-Py

Unity-Py is a Python client to simplify interactions with NASA's Unity Platform.

## Installation

### Install from Github
```
python -m pip install git+https://github.com/unity-sds/unity-py.git
```

### Building and installing locally using poetry

```
git clone https://github.com/unity-sds/unity-py.git
cd unity-py
poetry install
```

## Getting Started

### Authorization

Authorization can be handled interactively, in which case you will be prompted for a username/password when calling the Unity() method, or can be handled by way of environment variables:

```
export UNITY_USER=MY_UNITY_USERNAME
export UNITY_PASSWORD=MY_UNITY_PASSWORD
```

The order of Authentication Parameters is as follows:

1. Environment variables
2. Prompt for username and password

### Running your first command

```
from unity_py.unity import Unity
from unity_py.unity_session import UnitySession
from unity_py.unity_services import UnityServices as services

s = Unity()
dataManager = s.client(services.DATA_SERVICE)
collections = dataManager.get_collections()
print(collections)

cd = dataManager.get_collection_data(collections[0])
for dataset in cd:
    print(f'dataset name: {dataset.id}' )
    for f in dataset.datafiles:
        print("\t" + f.location)
```

## Testing
To run unit and regression tests:

```
# run all tests and include printouts:
poetry run pytest -s

# run non-regression tests:
poetry run pytest -m "not regression"

# run regression tests (and include logs)

```

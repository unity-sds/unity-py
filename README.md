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

## Testing
To run unit and regression tests:

```
# run all tests and include printouts:
poetry run pytest -s

# run non-regression tests:
poetry run pytest -m "not regression"

# run regression tests (and include logs)

```

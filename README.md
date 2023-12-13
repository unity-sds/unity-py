
<hr>

<div align="center">

![logo](https://user-images.githubusercontent.com/3129134/163255685-857aa780-880f-4c09-b08c-4b53bf4af54d.png)

<h1 align="center">Unity-Py</h1>

</div>

<pre align="center">A Python client to simplify interactions with NASA's Unity Platform.</pre>

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md) [![SLIM](https://img.shields.io/badge/Best%20Practices%20from-SLIM-blue)](https://nasa-ammos.github.io/slim/)

[INSERT SCREENSHOT OF YOUR SOFTWARE, IF APPLICABLE]

Unity-Py provides a seamless way to interact with NASA's Unity Platform using Python. Built to simplify the connection and data retrieval process, this client offers a programmatic interface to Unity's services.

## Features

* Pythonic interface to NASA's Unity Platform
* Support for interactive and environment variable-based authorization
  
## Contents

* [Quick Start](#quick-start)
* [Changelog](#changelog)
* [FAQ](#frequently-asked-questions-faq)
* [Contributing Guide](#contributing)
* [License](#license)
* [Support](#support)

## Quick Start

### Requirements

* Python
* pip
  
### Setup Instructions

1. Install via pypi:
   ```
   pip install unity-sds-client
   ```
2. Install from Github:
   ```
   python -m pip install git+https://github.com/unity-sds/unity-py.git
   ```
3. Building and installing locally using poetry:
   ```
   git clone https://github.com/unity-sds/unity-py.git
   cd unity-py
   poetry install
   ```

### Run Instructions

Authorization can be handled interactively, in which case you will be prompted for a username/password when calling the Unity() method, or can be handled by way of environment variables:
```
export UNITY_USER=MY_UNITY_USERNAME
export UNITY_PASSWORD=MY_UNITY_PASSWORD
```
Order of Authentication Parameters:
1. Environment variables
2. Prompt for username and password

### Usage Examples

```
from unity_sds_client.unity import Unity
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.unity_services import UnityServices as services

s = Unity()
# set the venue for interacting with venue specific services
# if your venue id is a single string, use the following
s.set_venue_id("unity-sips-test")

# otherwise set the project and venue:
# s.set_project("sbg")
# s.set_venue("dev")

dataManager = s.client(services.DATA_SERVICE)
collections = dataManager.get_collections()
print(collections)

cd = dataManager.get_collection_data(collections[0])
for dataset in cd:
    print(f'dataset name: {dataset.id}' )
    for f in dataset.datafiles:
        print("	" + f.location)
```

### Test Instructions

1. Run all tests and include printouts:
   ```
   poetry run pytest -s
   ```

2. Run non-regression tests:
   ```
   poetry run pytest -m "not regression"
   ```

3. Run regression tests (and include logs)
   ```
   (Not Available Yet)
   ```

## Changelog

See our [CHANGELOG.md](CHANGELOG.md) for a history of our changes.

See our [releases page](https://github.com/unity-sds/unity-py/releases) for our key versioned releases.

## Frequently Asked Questions (FAQ)

No questions yet. Propose a question to be added here by reaching out to our contributors! See support section below.

## Contributing

Interested in contributing to our project? Please see our: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

See our: [LICENSE](LICENSE)

## Support

Please reach out to [@anilnatha](https://github.com/anilnatha), [@mike-gangl](https://github.com/mike-gangl)

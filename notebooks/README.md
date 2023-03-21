# Notebooks

## mercury-dashboard.ipynb

An example notebook using the unity-py client to create a pseudo operator dashboard. Proof of concept and a way of defining what items need to be in the client, and what metadata/data services need to return.

### requirements
```
pip install mercury
pip install schemdraw[matplotlib]
```

## Running the example
export UNITY_USER = ***
export UNITY_PASSWORD = ***
mercury run mercury-dashboard.ipynb

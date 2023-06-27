# Unity-Py high level documentation

Documentation can be found <TBD>

## Quickstart

install unity-py

```
python -m pip install git+https://github.com/unity-sds/unity-py.git
```

And run some sample commands!

```
from unity_py.unity import Unity, Session

s = Session()
dataManager = s.client("DataManager")
collections = dataManager.get_collections()
print(collections)

cd = dataManager.get_collection_data(collections[0])
for dataset in cd:
    print(f'dataset name: {dataset.id}' )
    for f in dataset.datafiles:
        print("\t" + f.location)


```

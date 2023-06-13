from unity_py.unity_exception import UnityException
from unity_py.resources.dataset import Dataset
from unity_py.resources.data_file import DataFile
from pystac import Catalog, get_stac_version, ItemCollection
from pystac.errors import STACTypeError
import json

class Collection(object):
    """The Collection object contains metadata about a collection within the Unity system.
    """

    def __str__(self):
        return f'unity_py.resources.Collection(collection_id={self.collection_id})'

    def __repr__(self):
        return self.__str__()

    def __init__(self, id):
        self.collection_id = id
        self._datasets = []
        self._beginning_time = None
        self._ending_time = None

    def data_locations(self, type=[]):
        """
            A method to list all asset locations (data, metdata, etc)
            Parameters
            ----------
            type : List of Strings
                List of "stac asset keys" to filter on. commonly ["data"] is of most importance

            Returns
            -------
            locations
                List of returned asset locations
        """
        if len(type) == 0:
            return [file.location for files in [x.datafiles for x in self._datasets] for file in files]
        else:
            return [file.location for files in [x.datafiles for x in self._datasets] for file in files if file.type in type  ]



    def from_stac(stac_file):
        """
            A method for reading stac and converting it into a unity collection object. This is usually the result of a stage-in operation. stac formats supported are "GEOJSON Feature Collections" and STAC Catalogs with referenced item files.
            Parameters
            ----------
            stac_file : String
                The location of the stac file to read.

            Returns
            -------
            Collection
                A collection object including defined datasets

        """
        data = []
        id = None
        root_catalog = None

        try:

            try:
                root_catalog = Catalog.from_file(stac_file)
                id = root_catalog.id
                items = root_catalog.get_all_items()
            except STACTypeError as e:
                print("Trying stac items...")


            # ItemCollection
            if root_catalog is None:
                with open(stac_file, 'r') as f:
                    data = json.load(f)
                ic = ItemCollection.from_dict(data)
                id = ic.items[0].properties.get("collection", None)
                items = ic.items

            collection = Collection(id)
            # Catch file not found... ?
            for item in items:
                ds = Dataset(item.id, item.properties.get("collection"), item.properties.get("start_datetime",None), item.properties.get("end_datetime", None), item.properties.get("created", None))
                # Add other parameters/properties here
                # TODO
                # ds.add_property(key,value)

                for asset_key in item.assets:
                     asset = item.assets[asset_key]
                     ds.add_data_file(DataFile(asset_key ,asset.href))
                collection._datasets.append(ds)
            return collection
        except FileNotFoundError as fnfe:
            raise UnityException(str(fnfe))
        except STACTypeError as ste:
            raise UnityException(str(ste))
        except json.decoder.JSONDecodeError as jsd:
            raise UnityException(str(jsd))
        except:
            raise UnityException("An unknown error occured creating collection from stac")

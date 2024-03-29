from unity_sds_client.unity_exception import UnityException
from unity_sds_client.resources.dataset import Dataset
from unity_sds_client.resources.data_file import DataFile
from pystac import Catalog, get_stac_version, ItemCollection, Item, Asset
from pystac.errors import STACTypeError
import json
import os
from datetime import datetime
from datetime import timezone
from pystac import CatalogType
from dateutil import parser as date_parser

#import pytz

class Collection(object):
    """The Collection object contains metadata about a collection within the Unity system.
    """

    def __str__(self):
        return f'unity_sds_client.resources.Collection(collection_id={self.collection_id})'

    def __repr__(self):
        return self.__str__()

    def __init__(self, id):
        self.collection_id = id
        self._datasets = []
        self._beginning_time = None
        self._ending_time = None


    def add_dataset(self, dataset: Dataset):
        self._datasets.append(dataset)

    @property
    def datasets(self):
        """
        A method to return the included datasets from a collection object.

        Returns
            -------
            dataset
                List of dataset objects
        """
        return self._datasets
    
    def data_files(self, roles=[]):
        """
            A method to list all assets (data, metdata, etc)
            Parameters
            ----------
            type : List of Strings
                List of "stac asset roles" to filter on. commonly ["data"] is of most importance

            Returns
            -------
            files
                List of returned datafiles
        """
        if len(roles) == 0:
            return [file for files in [x.datafiles for x in self._datasets] for file in files]
        else:
            return [file for files in [x.datafiles for x in self._datasets] for file in files if set(file.roles).intersection(set(roles))]

    def data_locations(self, roles=[]):
        """
            A method to list all asset locations (data, metdata, etc)
            Parameters
            ----------
            type : List of Strings
                List of "stac asset roles" to filter on. commonly ["data"] is of most importance

            Returns
            -------
            locations
                List of returned asset locations
        """
        if len(roles) == 0:
            return [file.location for files in [x.datafiles for x in self._datasets] for file in files]
        else:
            return [file.location for files in [x.datafiles for x in self._datasets] for file in files if set(file.roles).intersection(set(roles))]

    def is_uri(path):
        if(path.startswith(tuple(["http:","https:","s3:"]))):
            return True
        else:
            return False

    def to_stac(collection, data_dir):
        """
            A method for writing stac and converting it from a unity collection object. The caller is responsible for providing a collection, datasets and datafiles along with the output location of the data.
            Parameters
            ----------
            collection : Collection
                The colleciton object to convert into stac catalog + stac item files.
            stac_file : String
                The location of the stac file to read.

        """
        # check data dir for a dangling "/"
        data_dir = data_dir.rstrip('/')

        catalog = Catalog(id=collection.collection_id, description="STAC Catalog")
        for dataset in collection._datasets:
            updated = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            item = Item(
                id=dataset.id,
                geometry=dataset.geometry,
                bbox=dataset.bbox,
                collection=dataset.collection_id,
                datetime = date_parser.parse(dataset.data_begin_time),
                properties={
                    "datetime": dataset.data_begin_time,
                    "start_datetime": dataset.data_begin_time,
                    "end_datetime":dataset.data_end_time,
                    "created": dataset.data_create_time if dataset.data_create_time!= None else updated,
                    "updated": updated
                },
            )
            item.properties.update(dataset.properties)
            catalog.add_item(item)

            for df in dataset.datafiles:
                
                if(Collection.is_uri(df.location)):
                    item_location = df.location
                else:
                    item_location = df.location.replace(data_dir, ".")

                key = item_location

                if key.startswith("./"):
                    key = os.path.basename(key)

                item.add_asset(
                    key = key,
                    asset = Asset(
                        href = item_location,
                        title = "{} file".format(df.type),
                        description = "",
                        roles = df.roles
                    )
                )

        from pystac.layout import TemplateLayoutStrategy
        write_dir = data_dir
        strategy = TemplateLayoutStrategy(item_template="")
        catalog.normalize_hrefs(write_dir,strategy=strategy)
        catalog.save(catalog_type=CatalogType.SELF_CONTAINED, dest_href=write_dir)


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
        stac_dir = os.path.abspath(os.path.dirname(stac_file))
        data = []
        id = None
        root_catalog = None

        try:

            try:
                root_catalog = Catalog.from_file(stac_file)
                id = root_catalog.id
                items = root_catalog.get_all_items()
            except STACTypeError as e:
                pass
                # attempt to read as a feature collection


            # ItemCollection
            if root_catalog is None:
                with open(stac_file, 'r') as f:
                    data = json.load(f)
                ic = ItemCollection.from_dict(data)
                try:
                    id = data['features'][0]['collection']
                except:
                    pass

                items = ic.items

            collection = Collection(id)
            # Catch file not found... ?
            for item in items:
                # if the id of the catalog and the id of the collection items are not the same,
                # then use the one that is a part of the collection item definition
                # Added 8/10/23
                ds = Dataset(item.id, id, item.properties.get("start_datetime", None),
                             item.properties.get("end_datetime", None), item.properties.get("created", None))
                if item.collection_id is not None and item.collection_id != id:
                     ds = Dataset(item.id, item.collection_id, item.properties.get("start_datetime", None),
                                 item.properties.get("end_datetime", None), item.properties.get("created", None))


                ds.bbox = item.bbox
                ds.geometry = item.geometry

                # Add other STAC properties to dataset properties
                ds.properties.update(item.properties)

                for asset_key in item.assets:

                    asset:Asset = item.assets[asset_key]
                    asset_type = asset.media_type if asset.media_type else ''
                    asset_roles = asset.roles if asset.roles is not None else []
                    asset_title = asset.title if asset.title is not None else ''
                    asset_description = asset.description if asset.description is not None else ''

                    if len(asset_roles) == 0 and asset_key in ["data", "metadata"]:
                        asset_roles = [asset_key]
                    
                    if(Collection.is_uri(asset.href)):
                        ds.add_data_file(DataFile(asset_type, asset.href, roles=asset_roles, title=asset_title, description=asset_description))
                    elif(os.path.isabs(asset.href)):
                        ds.add_data_file(DataFile(asset_type, asset.href, roles=asset_roles, title=asset_title, description=asset_description))
                    else:
                        ds.add_data_file(DataFile(asset_type, os.path.join(stac_dir, asset.href), roles=asset_roles, title=asset_title, description=asset_description))

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

import requests

from unity_sds_client.unity_exception import UnityException
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.resources.collection import Collection
from unity_sds_client.resources.dataset import Dataset
from unity_sds_client.resources.data_file import DataFile


class DataService(object):
    """
    The DataService class is a wrapper to the data endpoint(s) within Unity. This wrapper interfaces with the DAPA endpoints.

    The DataService class allows for the querying of data collections and data files within those collections.
    """

    def __init__(
        self,
        session: UnitySession,
        endpoint: str = None,
    ):
        """Initialize the DataService class.

        Parameters
        ----------
        session : UnitySession
            Description of parameter `session`.
        endpoint : str
            The endpoint used to access the data service API. This is usually
            shared across Unity Environments, but can be overridden. Defaults to
            "None", and will be read from the configuration if not set.

        Returns
        -------
        DataService
            the Data Service object.

        """
        self._session = session
        if endpoint is None:
            self.endpoint = self._session.get_unity_href()

    def get_collections(self, limit=10, output_stac=False):
        """Returns a list of collections

        Returns
        -------
        list
            List of returned collections

        """
        url = self.endpoint + "am-uds-dapa/collections"
        token = self._session.get_auth().get_token()
        response = requests.get(url, headers={"Authorization": "Bearer " + token}, params={"limit": limit})
        if output_stac:
            return response.json()

        # build collection objects here
        collections = []
        for data_set in response.json()['features']:
            collections.append(Collection(data_set['id']))

        return collections

    def get_collection_data(self, collection: type = Collection, limit=10, filter: str = None, output_stac=False):
        datasets = []
        url = self.endpoint + f'am-uds-dapa/collections/{collection.collection_id}/items'
        token = self._session.get_auth().get_token()
        params = {"limit": limit}
        if filter is not None:
            params["filter"] = filter
        response = requests.get(url, headers={"Authorization": "Bearer " + token}, params=params)
        if output_stac:
            return response.json()
        results = response.json()['features']
        
        for dataset in results:
            ds = Dataset(dataset['id'], collection.collection_id, dataset['properties']['start_datetime'], dataset['properties']['end_datetime'], dataset['properties']['created'], properties=dataset['properties'])

            for asset_key in dataset['assets']:
                location = dataset['assets'][asset_key]['href']
                file_type = dataset['assets'][asset_key].get('type', "")
                title = dataset['assets'][asset_key].get('title', "")
                description = dataset['assets'][asset_key].get('description', "")
                roles = dataset['assets'][asset_key]["roles"] if "roles" in dataset['assets'][asset_key] else ["metadata"] if asset_key in ['metadata__cmr','metadata__data'] else [asset_key]
                ds.add_data_file(DataFile(file_type, location, roles=roles, title=title, description=description))

            datasets.append(ds)

        return datasets

    def create_collection(self, collection: type = Collection, dry_run=False):

        # Collection must not be None
        if collection is None:
            raise UnityException("Invalid collection provided.")

        # test version Information?

        # Test collection ID name: project and venue
        if self._session._project is None or self._session._venue is None:
            raise UnityException("To create a collection, the Unity session Project and Venue must be set!")

        if not collection.collection_id.startswith(f"urn:nasa:unity:{self._session._project}:{self._session._venue}"):
            raise UnityException(f"Collection Identifiers must start with urn:nasa:unity:{self._session._project}:{self._session._venue}")

        collection = {
            "title": "Collection " + collection.collection_id,
            "type": "Collection",
            "id": collection.collection_id,
            "stac_version": "1.0.0",
            "description": "TODO",
            "providers": [
                {"name": "unity"}
            ],
            "links": [
                {
                    "rel": "root",
                    "href": "./collection.json?bucket=unknown_bucket&regex=%7BcmrMetadata.Granule.Collection.ShortName%7D___%7BcmrMetadata.Granule.Collection.VersionId%7D",
                    "type": "application/json",
                    "title": "test_file01.nc"
                },
                {
                    "rel": "item",
                    "href": "./collection.json?bucket=protected&regex=%5Etest_file.%2A%5C.nc%24",
                    "type": "data",
                    "title": "test_file01.nc"
                },
                {
                    "rel": "item",
                    "href": "./collection.json?bucket=protected&regex=%5Etest_file.%2A%5C.nc%5C.cas%24",
                    "type": "metadata",
                    "title": "test_file01.nc.cas"
                },
                {
                    "rel": "item",
                    "href": "./collection.json?bucket=private&regex=%5Etest_file.%2A%5C.cmr%5C.xml%24",
                    "type": "metadata",
                    "title": "test_file01.cmr.xml"
                }
            ],
            "stac_extensions": [],
            "extent": {
                "spatial": {
                    "bbox": [
                        [
                            0,
                            0,
                            0,
                            0
                        ]
                    ]
                },
                "temporal": {
                    "interval": [
                        [
                            "2022-10-04T00:00:00.000Z",
                            "2022-10-04T23:59:59.999Z"
                        ]
                    ]
                }
            },
            "license": "proprietary",
            "summaries": {
                "granuleId": [
                    "^test_file.*$"
                ],
                "granuleIdExtraction": [
                    "(^test_file.*)(\\.nc|\\.nc\\.cas|\\.cmr\\.xml)"
                ],
                "process": [
                    "stac"
                ]
            }
        }
        if not dry_run:
            url = self.endpoint + f'am-uds-dapa/collections'
            token = self._session.get_auth().get_token()
            response = requests.post(url, headers={"Authorization": "Bearer " + token},  json=collection)
            if response.status_code != 202:
                raise UnityException("Error creating collection: " + response.message)

    def define_custom_metadata(self, metadata: dict):
        if self._session._project is None or self._session._venue is None:
            raise UnityException("To add custom metadata, the Unity session Project and Venue must be set!")

        url = self.endpoint + f'am-uds-dapa/admin/custom_metadata/{self._session._project}'
        token = self._session.get_auth().get_token()
        response = requests.put(url, headers={"Authorization": "Bearer " + token},
                                params={"venue": self._session._venue}, json=metadata)
        if response.status_code != 200:
            raise UnityException("Error adding custom metadata: " + response.message)

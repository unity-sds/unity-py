import requests
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

    def get_collections(self):
        """Returns a list of collections

        Returns
        -------
        list
            List of returned collections

        """
        url = self.endpoint + "am-uds-dapa/collections"
        token = self._session.get_auth().get_token()
        response = requests.get(url, headers={"Authorization": "Bearer " + token})
        # build collection objects here
        collections = []
        for data_set in response.json()['features']:
            collections.append(Collection(data_set['id']))

        return collections

    def get_collection_data(self, collection: type= Collection):
        datasets = []
        url = self.endpoint + f'am-uds-dapa/collections/{collection.collection_id}/items'
        token = self._session.get_auth().get_token()
        response = requests.get(url, headers={"Authorization": "Bearer " + token})
        results = response.json()['features']
        
        for dataset in results:
            ds = Dataset(dataset['id'], collection.collection_id, dataset['properties']['start_datetime'], dataset['properties']['end_datetime'], dataset['properties']['created'])
            
            for asset_key in dataset['assets']:
                location = dataset['assets'][asset_key]['href']
                file_type = dataset['assets'][asset_key].get('type', "")
                title = dataset['assets'][asset_key].get('title', "")
                description = dataset['assets'][asset_key].get('description', "")
                roles = dataset['assets'][asset_key]["roles"] if "roles" in dataset['assets'][asset_key] else ["metadata"] if asset_key in ['metadata__cmr','metadata__data'] else [asset_key]
                ds.add_data_file(DataFile(file_type, location, roles=roles, title=title, description=description))

            datasets.append(ds)

        return datasets

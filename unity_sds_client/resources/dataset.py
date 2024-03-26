from unity_sds_client.resources.data_file import DataFile

class Dataset(object):
    """The Dataset object contains metadata about a collection within the Unity system, and also is a container for the data_files within a dataset.

    A Dataset can be made up of one or more files. A data file is the most common data_file wihtin a dataset. Other examples include metadata, browse imagery, checksums, etc.
    """

    def __str__(self):
        return f'unity_sds_client.resources.Dataset(data_id={self.id})'

    def __repr__(self):
        return self.__str__()

    def __init__(self, name, collection_id, start_time, end_time, creation_time, properties=None ):
        """Dataset object construction)

        Parameters
        ----------
        name : type
            Name of the dataset in the Unity system
        collection_id : str
            Collection identifer that this dataset belongs to
        start_time : type
            start time of the data coverage within the dataset
        end_time : type
            end time of the data coverage within the dataset
        creation_time : type
            The time a dataset was created

        Returns
        -------
        Dataset
            The dataset object

        """
        self.id = name
        self.collection_id = collection_id
        self.datafiles = []
        self.data_begin_time = start_time
        self.data_end_time = end_time
        self.data_create_time = creation_time
        self.properties = {}
        self.geometry = None
        self.bbox = None

        #add non-reserved properties
        if properties is not None:
            for key, value in properties.items():
                if key not in ['start_datetime','created', 'end_datetime']:
                    self.properties[key] = value

    def add_data_file(self, datafile: type=DataFile):
        """adds a data file to a dataset

        Parameters
        ----------
        datafile : DataFile
            a unity_sds_client.resource.datafile object containing the location of data products.

        """
        self.datafiles.append(datafile)

    def add_property(self, key, value):
        """adds a custom metadata property to a dataset

        Parameters
        ----------
        key : String
            The property name to be set
        Value : Object
            the property value to be set
        """
        self.properties[key] =  value

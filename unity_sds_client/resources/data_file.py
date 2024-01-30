class DataFile(object):
    """The Collection object contains metadata about a collection within the Unity system.
    """

    def __str__(self):
        return f'unity_sds_client.resources.DataFile(location={self.location},type={self.type})'

    def __repr__(self):
        return self.__str__()

    def __init__(self, type, location, title = "", description = "" ):
        self.type = type
        self.location = location
        self.title = title
        self.description = description

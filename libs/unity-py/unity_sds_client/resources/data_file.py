class DataFile(object):
    """The Collection object contains metadata about a collection within the Unity system.
    """

    def __str__(self):
        return f'unity_sds_client.resources.DataFile(location={self.location})'

    def __repr__(self):
        return self.__str__()

    def __init__(self, type, location, roles = [], title = "", description = "" ):
        self.description = description
        self.location = location
        self.roles = roles
        self.title = title
        self.type = type

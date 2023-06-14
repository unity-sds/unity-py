class DataFile(object):
    """The Collection object contains metadata about a collection within the Unity system.
    """

    def __str__(self):
        return f'unity_py.resources.DataFile(location={self.location})'

    def __repr__(self):
        return self.__str__()

    def __init__(self, type, location ):
        self.type = type
        self.location = location

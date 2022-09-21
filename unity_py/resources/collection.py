from unity_py.resources.dataset import Dataset

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

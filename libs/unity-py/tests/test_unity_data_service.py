from unity_sds_client.unity import Unity
from unity_sds_client.unity_exception import UnityException
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.resources.collection import Collection
from unity_sds_client.unity_services import UnityServices as Services

import pytest


@pytest.fixture
def cleanup_update_test():
    yield None
    print("Cleanup...")


def test_collection_creation(cleanup_update_test):
    #no venue, project
    with pytest.raises(UnityException):
        s = Unity()
        ds = s.client(Services.DATA_SERVICE)
        ds.create_collection(Collection("urn:nasa:unity:myproject:myvenue:identifier"), True)
    #no Venue
    with pytest.raises(UnityException):
        s = Unity()
        s.set_project("unity")
        ds = s.client(Services.DATA_SERVICE)
        ds.create_collection(Collection("urn:nasa:unity:myproject:myvenue:identifier"), True)
    #null collections
    # does not match name
    with pytest.raises(UnityException):
        s = Unity()
        s.set_project("unity")
        s.set_venue("test")
        ds = s.client(Services.DATA_SERVICE)
        ds.create_collection(None, True)

    #does not match name
    with pytest.raises(UnityException):
        s = Unity()
        s.set_project("unity")
        s.set_venue("test")
        ds = s.client(Services.DATA_SERVICE)
        ds.create_collection( Collection("urn:nasa:unity:myproject:myvenue:identifier"), True)

        # does not match name
    s = Unity()
    s.set_project("unity")
    s.set_venue("test")
    ds = s.client(Services.DATA_SERVICE)
    ds.create_collection(Collection("urn:nasa:unity:unity:test:my_collection_id"), True)
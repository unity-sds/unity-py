from unity_sds_client.unity import Unity
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.unity_services import UnityServices as services

import pytest

@pytest.fixture
def cleanup_update_test():
    yield None
    print("Cleanup...")


def test_default_unity_client():
    client = Unity()
    assert True == True

@pytest.mark.regression
def test_example_regression_test(cleanup_update_test):
    print("Example regression test")
    s = Unity()
    dataManager = s.client(services.DATA_SERVICE)
    collections = dataManager.get_collections()
    assert len(collections) > 0

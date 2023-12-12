from unity_sds_client.unity import Unity
from unity_sds_client.unity_exception import UnityException
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.unity_services import UnityServices as Services

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
    print("Example collection test")
    s = Unity()
    dataManager = s.client(Services.DATA_SERVICE)
    collections = dataManager.get_collections()
    assert len(collections) > 0


@pytest.mark.regression
def test_example_process(cleanup_update_test):
    print("Example process test")
    s = Unity()
    s.set_venue_id("unity-sips-test")
    process_manager = s.client(Services.PROCESS_SERVICE)
    processes = process_manager.get_processes()
    for p in processes:
        print(p)
    assert len(processes) > 0


@pytest.mark.regression
def test_venue_id_exception(cleanup_update_test):
    with pytest.raises(UnityException):
        s = Unity()
        process_manager = s.client(Services.PROCESS_SERVICE)


"""
This module contains a set of tests is to ensure that the
Unity Health Service is functional.
"""

import pytest

from unity_sds_client.unity import Unity
from unity_sds_client.unity_services import UnityServices


@pytest.fixture
def cleanup_update_test():
    yield None
    print("Cleanup...")

@pytest.mark.regression
def test_health_service_client_creation(cleanup_update_test):
    """
    Test that an instance of the health service can be instantiated.
    """
    s = Unity()
    health_service = s.client(UnityServices.HEALTH_SERVICE)

@pytest.mark.regression
def test_health_status_retrieval(cleanup_update_test):
    """
    Test that health statuses can be retrieved from the health service.
    """
    print("Example health status check")
    s = Unity()
    health_service = s.client(UnityServices.HEALTH_SERVICE)
    heatlh_statuses = health_service.get_health_status()
    assert heatlh_statuses is not None

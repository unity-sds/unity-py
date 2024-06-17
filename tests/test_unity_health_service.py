"""
This module contains a set of tests is to ensure that the
Unity Health Service is functional.
"""

import pytest

from unity_sds_client.unity import Unity
from unity_sds_client.unity_services import UnityServices


@pytest.mark.regression
def test_health_service_client_creation():
    """
    Test that an instance of the health service can be instantiated.
    """
    s = Unity()
    health_service = s.client(UnityServices.HEALTH_SERVICE)

@pytest.mark.regression
def test_health_status_retrieval():
    """
    Test that health statuses can be retrieved using the health service.
    """
    print("Example health status check")
    s = Unity()
    health_service = s.client(UnityServices.HEALTH_SERVICE)
    health_statuses = health_service.get_health_status()
    assert health_statuses is not None

@pytest.mark.regression
def test_health_status_printing():
    """
    Test that health statuses can be printed using the health service.
    """
    print("Example health status check")
    s = Unity()
    health_service = s.client(UnityServices.HEALTH_SERVICE)
    health_service.print_health_status()
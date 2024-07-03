from enum import Enum


class UnityServices(Enum):
    """
    The UnityServices class is used to specify a service, when needed, when interacting with the unity_sds_client package.
    """

    APPLICATION_SERVICE = "app_service"
    DATA_SERVICE = "data_service"
    HEALTH_SERVICE = "health_service"
    PROCESS_SERVICE = "process_service"

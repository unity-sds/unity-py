from enum import Enum


class UnityServices(Enum):
    """
    The UnityServices class is used to specify a service, when needed, when interacting with the unity_py library.
    """

    DATA_SERVICE = "data_service"
    APPLICATION_SERVICE = "app_service"
    JOB_SERVICE = "job_service"
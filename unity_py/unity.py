import os
from configparser import ConfigParser, ExtendedInterpolation
from unity_py.data_manager import DataManager
from unity_py.unity_session import UnitySession
from unity_py.unity_exception import UnityException
from unity_py.unity_environments import UnityEnvironments


class Unity(object):
    """
    The Unity class is used to create services and resources that facilitate interacting with the Unity Platform.
    Basic shared configuration items are also saved here. This wraps an underlying unity_session.Session object, which
    is passed to different services and resources as needed.
    """

    def __init__(self, environment: UnityEnvironments = UnityEnvironments.TEST):
        """
        :param environment: the default environment for a session to work with. Defaults to 'TEST' unity environment.
        """
        env = environment
        config = _read_config([
            os.path.dirname(os.path.realpath(__file__)) + "/unity.{}.cfg".format(env.value)
        ])
        self._session = UnitySession(env, config)

    def client(self, service_name: str):
        """
        :param service_name - the desired service, such as DataManager, JobManager, ApplicationManager.
        """
        if service_name == "DataManager":
            return DataManager(session=self._session)
        else:
            raise UnityException("Invalid service name: " + service_name)


def _read_config(config_files):
    config = ConfigParser(interpolation=ExtendedInterpolation())

    for config_file in config_files:
        if config_file is not None:
            with open(config_file) as source:
                config.read_file(source)

    return config


def _get_config(config, section, setting):
    return config.get(section.upper(), setting)

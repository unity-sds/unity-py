import os
from configparser import ConfigParser, ExtendedInterpolation
from unity_sds_client.services.data_service import DataService
from unity_sds_client.services.process_service import ProcessService
from unity_sds_client.services.health_service import HealthService
from unity_sds_client.unity_session import UnitySession
from unity_sds_client.unity_exception import UnityException
from unity_sds_client.unity_environments import UnityEnvironments
from unity_sds_client.unity_services import UnityServices


class Unity(object):
    """
    The Unity class is used to create services and resources that facilitate interacting with the Unity Platform.
    Basic shared configuration items are also saved here. This wraps an underlying unity_session.Session object, which
    is passed to different services and resources as needed.
    """

    def __init__(self, environment: UnityEnvironments = UnityEnvironments.TEST, config_file_override:str = None):
        """
        :param environment: the default environment for a session to work with. Defaults to 'TEST' unity environment.
        :param config_file_override: absolute path to a config file containing settings to override default config
        """
        env = environment
        config = _read_config([
            os.path.dirname(os.path.realpath(__file__)) + "/envs/environments.cfg".format(str(env.value).lower()),
            config_file_override
        ])
        self._session = UnitySession(env.value, config)

    def set_project(self, project):
        """
        :param project: the project to use when interacting with venue specific services. Used in building the restful
        endpoint.
        """
        self._session._project  = project

    def set_venue(self, venue):
        """
        :param venue: the venue to use when interacting with venue specific services. Used in building the restful
        endpoint.
        """
        self._session._venue = venue

    def set_venue_id(self, venue_id):
        """
        :param venue_id: explicitly name the venue identifier. Useful for legacy or non-hierarchical venue ids.  Used in
         building the restful
        endpoint.
        """
        self._session._venue_id = venue_id

    def client(self, service_name: UnityServices):
        """
        :param service_name - the desired service, such as UnityServices.APPLICATION_SERVICE, UnityServices.DATA_SERVICE, or UnityServices.PROCESS_SERVICE.
        """
        if service_name == UnityServices.DATA_SERVICE:
            return DataService(session=self._session)
        if service_name == UnityServices.HEALTH_SERVICE:
            return HealthService(session=self._session)
        elif service_name == UnityServices.PROCESS_SERVICE:
            return ProcessService(session=self._session)
        else:
            raise UnityException("Invalid service name: " + str(service_name))

    def __str__(self):
        response = "\nUNITY CONFIGURATION"
        response = response + "\n" + len(response) * "-" + "\n"
        
        config = self._session.get_config()
        config_sections = config.sections()
        for section in config_sections:
            response = response + "\n[{}]\n".format(section)
            for setting in dict(config[section]):
                response = response + "{}: {}\n".format(setting, dict(config[section])[setting])

        response = response + self.client(UnityServices.HEALTH_SERVICE).generate_health_status_report()

        return response


def _read_config(config_files):
    config = ConfigParser(interpolation=ExtendedInterpolation())

    for config_file in config_files:
        if config_file is not None:
            with open(config_file) as source:
                config.read_file(source)

    return config


def _get_config(config, section, setting):
    return config.get(section.upper(), setting)

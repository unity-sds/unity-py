import os
import requests
from configparser import ConfigParser, ExtendedInterpolation
from unity_py.data_manager import DataManager
from unity_py.unity_session import UnitySession
from unity_py.unity_exception import UnityException

class Session(object):
    """
    Session is a user can create services and resources. Basic shared configuration items
    are also saved here. This wraps an underlying unity_session.Session object, which
    is passed to different services and resources as needed.
    """

    def __init__(self, environment: str = "test"):
        """
        :param environment: the defualt environment for a session to work with. Defaults to 'TEST' unity environment.
        """
        env = environment
        config = _read_config([
            os.path.dirname(os.path.realpath(__file__)) + "/unity."+env+".cfg",
        ])
        self._session = UnitySession(env, config)

    def client(self, service_name: str):
        """
        :param resource - the desired service, such as DataManager, JobManager, ApplicationManager.
        """
        if service_name == "DataManager":
            return DataManager(session=self._session)
        else:
            raise UnityException("Invalid service name: " + service_name)


class Unity(object):
    """
    The intention of the Unity Python class is to help the user get the most out of
    using Unity without needing to worry about the details about *how* to interact with Unity
    services. This is achieved by a default set of configuration settings, overridable by the user,
    and methods that expose the available Unity operations.
    """

    def __init__(self, config_file: str = None):
        """
        :param config_file: The path to a configuration settings file that
        includes settings the user wants to override. The user may choose to override
        one or more settings.  See `unity.cfg` for the list of settings that may be overridden.
        """

        # Read Unity Configuration Settings, if a user_config exists, any settings
        # specified in it will take precedence over the respective settings in the
        # default config
        self._config = _read_config([
            os.path.dirname(os.path.realpath(__file__)) + "/unity.cfg",
            config_file,
        ])

    def __str__(self):
        response = "UNITY CONFIGURATION"
        response = response + "\n\n" + len(response) * "-" + "\n\n"

        for section in self._config.sections():
            response = response + "{}:{}\n".format(section, dict(self._config[section]))

        return response

    def submit_job(self, app_name: str, job_config: str) -> str:
        """
        Submit a job that will run a process using the Science Processing Service (SPS).
        :param app_name: The name of the application that this job is executing.
        :param job_config: A json formatted string specifying details about this job.
        :return: The job-id if the job is successfully submitted.
        """

        headers = {
            'Content-type': 'application/json'
        }

        try:
            job_url = _get_config(self._config, 'jobs', 'sps_job_submission_endpoint').format(app_name)
            r = requests.post(job_url, headers=headers, json=job_config)

            job_location = r.headers['location']

            # Hack to remove localhost domain/port until this can be updated in the WPST API
            if "http://127.0.0.1:5000" in job_location:
                job_location = job_location.replace(
                    "http://127.0.0.1:5000",
                    _get_config(self._config, 'jobs', 'sps_wpst_domain')
                )

            job_id = job_location.replace(job_url + "/", "")

        except requests.exceptions.HTTPError as e:
            # Add Logging Mechanism
            raise

        return job_id

    def get_job_status(self, app_name: str, job_id: str) -> str:
        """
        Get the status of a job that was submitted to the Science Processing System (SPS)
        :param app_name: The name of the application that this job is executing.
        :param job_id: The job-id of the job for which the status is being requested
        :return: The status of the job
        """

        try:

            job_status_url = _get_config(self._config, 'jobs', 'sps_job_status_endpoint').format(app_name, job_id)
            response = requests.get(job_status_url)
            job_status = response.json()['status']

        except requests.exceptions.HTTPError as e:
            # Add Logging Mechanism
            raise

        return job_status


def _read_config(config_files):
    config = ConfigParser(interpolation=ExtendedInterpolation())

    for config_file in config_files:
        if config_file is not None:
            with open(config_file) as source:
                config.read_file(source)

    return config


def _get_config(config, section, setting):
    return config.get(section.upper(), setting)

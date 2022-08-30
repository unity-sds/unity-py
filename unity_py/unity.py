import os
import requests
from configparser import ConfigParser, ExtendedInterpolation

DEFAULT_CONFIG = os.path.dirname(os.path.realpath(__file__)) + "/unity.cfg"


class Unity(object):

    def __init__(self, user_config=None):

        # Read Unity Configuration Settings, if a user_config exists, any settings
        # specified in it will take precedence over the respective settings in the
        # default config
        self._config = read_config([
            os.path.dirname(os.path.realpath(__file__)) + "/unity.cfg",
            user_config,
        ])

    def __str__(self):
        response = "UNITY CONFIGURATION"
        response = response + "\n\n" + len(response) * "-" + "\n\n"

        for section in self._config.sections():
            response = response + "{}:{}\n".format(section, dict(self._config[section]))

        return response

    def submit_job(self, app_name, job_config):

        headers = {
            'Content-type': 'application/json'
        }

        try:
            job_url = get_config(self._config, 'jobs', 'sps_job_submission_endpoint').format(app_name)
            r = requests.post(job_url, headers=headers, json=job_config)

            job_location = r.headers['location']

            # Hack to remove localhost domain/port until this can be updated in the WPST API
            if "http://127.0.0.1:5000" in job_location:
                job_location = job_location.replace("http://127.0.0.1:5000", get_config(self._config,'jobs','sps_wpst_domain'))

            job_id = job_location.replace(job_url + "/", "")

        except requests.exceptions.HTTPError as e:
            # Add Logging Mechanism
            raise

        return job_id

    def get_job_status(self, app_name, job_id):

        try:

            job_status_url = get_config(self._config, 'jobs', 'sps_job_status_endpoint').format(app_name, job_id)
            response = requests.get(job_status_url)
            job_status = response.json()['status']

        except requests.exceptions.HTTPError as e:
            # Add Logging Mechanism
            raise

        return job_status


def read_config(config_files):
    config = ConfigParser(interpolation=ExtendedInterpolation())

    for config_file in config_files:
        if config_file is not None:
            with open(config_file) as source:
                config.read_file(source)

    return config


def get_config(config, section, setting):
    return config.get(section.upper(), setting)

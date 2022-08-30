import os
from configparser import ConfigParser

DEFAULT_CONFIG = os.path.dirname(os.path.realpath(__file__)) + "/unity.cfg"


class Unity(object):

    def __init__(self, user_config=None):
        self._config = read_config([DEFAULT_CONFIG, user_config])

    def __str__(self):
        response = "UNITY CONFIGURATION"
        response = response + "\n\n" + len(response) * "-" + "\n\n"

        for section in self._config.sections():
            response = response + "{}:{}\n".format(section, dict(self._config[section]))

        return response


def read_config(config_files):
    config = ConfigParser()

    for config_file in config_files:
        if config_file is not None:
            with open(config_file) as source:
                config.read_file(source)

    return config


def get_config(config, section, setting):
    return config.get(section.upper(), setting)

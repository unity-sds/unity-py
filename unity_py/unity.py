import os
from configparser import ConfigParser

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


def read_config(config_files):
    config = ConfigParser()

    for config_file in config_files:
        if config_file is not None:
            with open(config_file) as source:
                config.read_file(source)

    return config


def get_config(config, section, setting):
    return config.get(section.upper(), setting)

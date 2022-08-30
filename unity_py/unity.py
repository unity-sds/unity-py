import os
from configparser import ConfigParser

DEFAULT_CONFIG = os.path.dirname(os.path.realpath(__file__)) + "/unity.cfg"


class Unity(object):

    def __init__(self, user_config=None):
        self._config = read_config([DEFAULT_CONFIG, user_config])


def read_config(config_files):
    config = ConfigParser()

    for config_file in config_files:
        if config_file is not None:
            with open(config_file) as source:
                config.read_file(source)

    return config

import os
from yaml import load, dump

import logging

"""
Contains the standard settings which are saved to a yaml on first start, after that the yaml file is loaded.
"""


class Settings(object):
    def __init__(self):
        self.__settings_file = "settings.yaml"

        if not os.path.isfile(self.__settings_file) or not self.load_setting():
            self.__settings_values = {
                "log_dir": "Logs",
                "last_selected_dir": "test",
                "last_flow": "flow.current",
                "max_log_history_days": 5
            }
            self.save_setting()

    @property
    def log_dir(self) -> str:
        return self.__settings_values["log_dir"]

    @property
    def last_selected_dir(self) -> str:
        return self.__settings_values["last_selected_dir"]

    @property
    def last_flow(self) -> str:
        return self.__settings_values["last_flow"]

    @last_flow.setter
    def last_flow(self, file_name: str):
        self.__settings_values["last_flow"] = file_name

    @property
    def max_log_history_days(self) -> str:
        return self.__settings_values["max_log_history_days"]


    def save_setting(self):
        with open(self.__settings_file, 'w') as stream:
            dump(self.__settings_values, stream, default_flow_style=False)

    def load_setting(self):
        with open(self.__settings_file, 'r') as stream:
            self.__settings_values = load(stream)
            if self.__settings_values is None:
                return False
            elif len(self.__settings_values) is 0:
                return False
            return True

    @property
    def settings_file(self):
        return self.__settings_file

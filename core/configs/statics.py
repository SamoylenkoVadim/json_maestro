import logging
import os
from json import JSONDecodeError
from typing import Any
from logging import ERROR

import json
import yaml

import core.logging_utils.logger_constants as log_const


logger = logging.getLogger(log_const.SYSTEM_LOGGER_NAME)


class Statics:
    def __init__(self, path, **kwargs):
        self._path = path
        self._data = self.load_data()

    def __getitem__(self, item):
        return self._data[item]

    def __repr__(self):
        return str(self._data)

    def items(self):
        return self._data.items()

    def load_data(self) -> dict[Any, Any]:
        result = {}
        os.chdir(self._path)
        for file in os.listdir(self._path):
            try:
                self.load_file(file, result)
            except (FileNotFoundError, UnicodeDecodeError, JSONDecodeError):
                logger.log(ERROR, f"Failed to load file {file}.", exc_info=True)
        return result

    def load_file(self, file, result):
        raise NotImplementedError


class StaticsJson(Statics):
    extensions = (".json",)

    def __init__(self, path, json_type, **kwargs):
        self.json_type = json_type
        super().__init__(path, **kwargs)

    def load_file(self, file: str, result: dict):
        file_name, file_ext = os.path.splitext(file)
        if file_ext in self.extensions and \
                (self.json_type == "all" or file_name == self.json_type):
            with open(file) as f:
                data = json.load(f)
                for key, value in data.items():
                    if value.get("enabled", True):
                        result[key] = value


class StaticsYaml(Statics):
    extensions = (".yml", ".yaml")

    def load_file(self, file: str, result: dict):
        file_name, file_ext = os.path.splitext(file)
        if file_ext in self.extensions:
            with open(file) as f:
                data = yaml.full_load(f)
                result[file_name] = data

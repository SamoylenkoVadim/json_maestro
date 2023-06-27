from typing import Dict, Any, Optional
import core.logging_utils.logger_constants as log_const


class BaseASL:
    version: Optional[int]
    id: Optional[str]

    def __init__(self, items: Dict[str, Any], id: Optional[str] = None):
        items = items or {}
        self.version = items.get("version", -1)
        self.id = id
        self.key_name_value = None  # define in child classes


    def _log_params(self) -> dict:
        return {
            "asl_class": self.__class__.__name__,
            log_const.KEY_NAME: self.key_name_value
        }

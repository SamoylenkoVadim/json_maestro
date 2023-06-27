from typing import Union
import json
from fl.asl_models.exc_handling import exc_handler


@exc_handler
def from_bytes_or_str(value: Union[bytes, str]) -> dict:
    if isinstance(value, bytes):
        return json.loads(value.decode("utf-8"))
    else:
        return json.loads(value)


@exc_handler
def to_bytes(value: dict) -> bytes:
    return json.dumps(value).encode("utf-8")


@exc_handler
def to_str(value: dict) -> str:
    return json.dumps(value)
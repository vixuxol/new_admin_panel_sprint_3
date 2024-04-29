import json

from typing import Any
from common.state_storage.base_storage import BaseStorage



class JsonFileStorage(BaseStorage):
    """Implementation of a storage using a local file.
    Storage format: JSON
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: dict[str, Any]) -> None:
        """Save state in storage"""
        with open(self.file_path, "w+") as json_storage:
            json.dump(state, json_storage)
            

    def retrieve_state(self) -> dict[str, Any]:
        """Get state from storage"""
        try:
            with open(self.file_path, "r+") as json_storage:
                return json.load(json_storage)
        except FileNotFoundError:
            return {}
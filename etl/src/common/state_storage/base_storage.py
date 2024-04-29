from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStorage(ABC):
    @abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save state in storage"""
        raise NotImplementedError

    @abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Get state from storage"""
        raise NotImplementedError
from typing import Protocol, Dict, Any

class SystemProperty(Protocol):
    """
    A protocol representing system properties.
    """
    os_name: str

    def __init__(self, os_name: str) -> None:
        """
        Initialize the SystemProperty with the given OS name.
        """
        self._os_name: str = os_name

    def get_all(self) -> Dict[str, Any]:
        """
        Get all system properties.
        """
        if self._os_name == "Linux":
            return self._get_all_linux()
        elif self._os_name == "Windows":
            return self._get_all_win()
        else:
            return {"status": "NOK", "message": "Unknown operating system"}

    def _get_all_linux(self) -> Dict[str, Any]:
        """
        Get all system properties for Linux.
        """
        return {}

    def _get_all_win(self) -> Dict[str, Any]:
        """
        Get all system properties for Windows.
        """
        return {}


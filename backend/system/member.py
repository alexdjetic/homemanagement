from .system import execute
from typing import List, Dict, Any

class Member:
    """Utility class for managing group members.

    This class provides static methods for adding and removing users from groups.

    Functions (Methods):
        - add_member_to_group: Add a user to a group.
        - remove_member_from_group: Remove a user from a group.
        - get_group_members: Get all members of a group.
    """

    @staticmethod
    async def add_member_to_group(groupname: str, username: str) -> dict:
        """Add a user to a group.

        Args:
            groupname (str): The name of the group.
            username (str): The name of the user to add.

        Returns:
            dict: A dictionary containing status, message, error, and stdout.
        """
        try:
            output, error, status = await execute(f"usermod -aG {groupname} {username}")
            if status == 0:
                return {
                    "status": 200,
                    "message": f"The user {username} was successfully added to the group {groupname}.",
                    "error": error,
                    "stdout": output
                }
            else:
                return {
                    "status": 500,
                    "message": f"Failed to add the user {username} to the group {groupname}.",
                    "error": error,
                    "stdout": output
                }
        except Exception as e:
            return {
                "status": 501,
                "message": str(e),
                "error": error,
                "stdout": output
            }

    @staticmethod
    async def remove_member_from_group(groupname: str, username: str) -> dict:
        """Remove a user from a group.

        Args:
            groupname (str): The name of the group.
            username (str): The name of the user to remove.

        Returns:
            dict: A dictionary containing status, message, error, and stdout.
        """
        try:
            output, error, status = await execute(f"gpasswd -d {username} {groupname}")
            if status == 0:
                return {
                    "status": 200,
                    "message": f"The user {username} was successfully removed from the group {groupname}.",
                    "error": error,
                    "stdout": output
                }
            else:
                return {
                    "status": 500,
                    "message": f"Failed to remove the user {username} from the group {groupname}.",
                    "error": error,
                    "stdout": output
                }
        except Exception as e:
            return {
                "status": 501,
                "message": str(e),
                "error": error,
                "stdout": output
            }
    
    @staticmethod
    async def get_group_members(groupname: str) -> List[str]:
        """Get all members of a group."""
        try:
            output, error, status = await execute(f"getent group {groupname}")
            if status == 0:
                parts = output.split(":")
                if len(parts) >= 4:
                    return parts[3].split(",")
            return []
        except Exception as e:
            return []

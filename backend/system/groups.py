from typing import Dict, Any
from .system import execute, exec_powershell
from .system_property import SystemProperty
from .member import Member

class Groups(SystemProperty):
    """Module for managing system groups.

    This module provides functionality for retrieving information about system groups
    on both Linux and Windows operating systems.

    Attributes:
        None

    Functions (Methods):
        - __init__: Initialize Groups class.
        - _get_all_linux: Retrieve information about all groups on a Linux system.
        - _get_all_win: Retrieve information about all groups on a Windows system.
        - _parse_group_entry: Parse a single entry of group information.
        - _parse_windows_group_entry: Parse a single entry of group information from a Windows system.
        - del_group: Delete a group from the system.
        - add_group: Add a new group to the system.
        - add_member: Add members to a group.
        - remove_member: Remove a member from a group.
    """

    def __init__(self, os_name: str):
        """Initialize Groups class.

        Args:
            os_name (str): The name of the operating system.
        """
        super().__init__(os_name)

    async def _get_all_linux(self) -> Dict[str, Any]:
        """Retrieve information about all groups on a Linux system.

        Returns:
            dict: A dictionary containing information about all groups.
        """
        output, error, status = await execute("cat /etc/group")
        data: dict = {"status": status, "groups": {}}

        if status == 0:
            groups: dict = {}

            for line in output.split("\n"):
                group_info: dict = self._parse_group_entry(line)
                if group_info:
                    groups[group_info["Group_Name"]] = group_info

            data["groups"] = groups
        else:
            data["groups"] = None

        return data

    def _parse_group_entry(self, entry: str) -> Dict[str, Any]:
        """Parse a single entry of group information.

        Args:
            entry (str): A single line containing group information.

        Returns:
            dict: A dictionary containing parsed group information.
        """
        parts = entry.split(":")

        if len(parts) >= 4:
            return {
                "Group_Name": parts[0],
                "GID": parts[2],
                "Members": parts[3].split(","),
            }

        return {}

    async def _get_all_win(self) -> Dict[str, Any]:
        """Retrieve information about all groups on a Windows system.

        Returns:
            dict: A dictionary containing information about all groups.
        """
        output, error, status = await exec_powershell("Get-LocalGroup | Select-Object Name, Description, GroupCategory, SID")
        data = {"status": status}

        if status == 0:
            groups = {}
            lines = output.strip().split("\n")
            for line in lines[2:]:
                group_info = self._parse_windows_group_entry(line)
                if group_info:
                    groups[group_info["Name"]] = group_info
            data["groups"] = groups
        else:
            data["groups"] = None

        return data

    def _parse_windows_group_entry(self, entry: str) -> Dict[str, Any]:
        """Parse a single entry of group information from a Windows system.

        Args:
            entry (str): A single line containing group information.

        Returns:
            dict: A dictionary containing parsed group information.
        """
        parts = entry.strip().split()
        if len(parts) >= 4:
            return {
                "Name": parts[0],
                "Description": parts[1],
                "GroupCategory": parts[2],
                "SID": parts[3],
            }
        return {}

    async def del_group(self, groupname: str) -> Dict[str, Any]:
        """Delete a group from the system.

        Args:
            groupname (str): The name of the group to delete.

        Returns:
            dict: A dictionary containing status and message.
        """
        try:
            output, error, status = await execute(f"groupdel {groupname}")
            if status == 0:
                return {
                    "status": 200,
                    "message": f"The group {groupname} was successfully deleted.",
                    "error": error,
                    "stdout": output
                }
            else:
                return {
                    "status": 500,
                    "message": f"Failed to delete the group {groupname}.",
                    "error": error,
                    "stdout": output
                }
        except Exception as e:
            return {"status": 501, "message": str(e)}

    async def add_group(self, groupname: str) -> Dict[str, Any]:
        """Add a new group to the system.

        Args:
            groupname (str): The name of the group to add.

        Returns:
            dict: A dictionary containing status and message.
        """
        try:
            output, error, status = await execute(f"groupadd {groupname}")
            if status == 0:
                return {
                    "status": 200,
                    "message": f"The group {groupname} was successfully created.",
                    "error": error,
                    "stdout": output
                }
            else:
                return {
                    "status": 500,
                    "message": f"Failed to create the group {groupname}.",
                    "error": error,
                    "stdout": output
                }
        except Exception as e:
            return {"status": 501, "message": str(e)}

    @staticmethod
    async def get_group(groupname: str) -> Dict[str, Any]:
        """Get information about a specific group."""
        try:
            output, error, status = await execute(f"getent group {groupname}")
            if status == 0:
                parts = output.strip().split(":")
                if len(parts) >= 4:
                    return {
                        "Name": parts[0],
                        "Description": parts[1],
                        "GroupCategory": parts[2],
                        "SID": parts[3],
                        "Members": await Member.get_group_members(groupname)
                    }
            return {}
        except Exception as e:
            return {"error": str(e)}

    async def add_member(self, groupname: str, username: str) -> Dict[str, Any]:
        """Add members to a group.

        Args:
            groupname (str): The name of the group.
            username (str): The name of the user to add to the group.

        Returns:
            dict: A dictionary containing status, message, error, and stdout.
        """
        return await Member.add_member_to_group(groupname, username)

    async def remove_member(self, groupname: str, username: str) -> Dict[str, Any]:
        """Remove a member from a group.

        Args:
            groupname (str): The name of the group.
            username (str): The name of the user to remove from the group.

        Returns:
            dict: A dictionary containing status, message, error, and stdout.
        """
        return await Member.remove_member_from_group(groupname, username)
    

####################################################################################
# Author: Djetic Alexandre
# Description: This is a class to manage User of an os_name
####################################################################################

import psutil
from typing import Dict, Any
from .system import execute, get_os
from .system_property import SystemProperty

class Users(SystemProperty):
    """Module for managing system users.

    This module provides functionality for retrieving information about system users
    on Linux operating systems.

    Classes:
        Users: A class for managing system users.

    Attributes:
        None

    Functions (Methods):
        - __init__: Initialize Users class.
        - _get_all_linux: Retrieve information about all users on a Linux system.
        - _parse_passwd_output: Parse the output of the /etc/passwd file from a Linux system.
    """

    def __init__(self, os_name: str):
        """Initialize Users class.

        Args:
            os_name (str): The name of the operating system.

        Returns:
            None
        """
        super().__init__(os_name)

    @staticmethod
    async def get_user(username: str) -> dict:
        """Retrieve information about a specific user.

        Args:
            username (str): The username of the user to retrieve information for.

        Returns:
            dict: A dictionary containing information about the user.
        """
        try:
            output, error, status = await execute(f"getent passwd {username}")

            if status == 0:
                parts = output.split(":")
                if len(parts) >= 6:
                    uid = parts[2]
                    gid = parts[3]
                    full_name = parts[4].split(",")[0]
                    home_dir = parts[5]
                    shell = parts[6].strip()

                    return {
                        "username": username,
                        "uid": uid,
                        "gid": gid,
                        "full_name": full_name,
                        "home_dir": home_dir,
                        "shell": shell,
                        "login": Users.is_login(username)
                    }
                else:
                    return {"status": 404, "message": "User not found"}
            else:
                return {"status": 500, "message": error}
        except Exception as e:
            return {"status": 500, "message": str(e)}

    async def _get_all_linux(self) -> dict:
        """Retrieve information about all users on a Linux system.

        Returns:
            dict: A dictionary containing information about all users.
        """
        try:
            output, error, status = await execute("cat /etc/passwd")
            if status == 0:
                data = {"status": 200, "users": self._parse_passwd_output(output)}
            else:
                data = {"status": 500, "message": error}
            return data
        except Exception as e:
            return {"status": "NOK", "message": str(e)}

    def _parse_passwd_output(self, output: str) -> dict:
        """Parse the output of the /etc/passwd file from a Linux system.

        Args:
            output (str): The contents of the /etc/passwd file.

        Returns:
            dict: A dictionary containing parsed user information.
        """
        users = {}

        for line in output.splitlines():
            parts = line.split(':')

            if len(parts) >= 7:
                username = parts[0]
                uid = parts[2]
                gid = parts[3]
                full_name = parts[4]
                home_dir = parts[5]
                shell = parts[6]

                users[username] = {
                    "username": username,
                    "uid": uid,
                    "gid": gid,
                    "full_name": full_name,
                    "home_dir": home_dir,
                    "shell": shell,
                    "login": Users.is_login(username)
                }

        return users

    async def add_user(self, username: str, full_name: str, homedir: str, shell: str) -> dict:
        """Add a new user to the system.

        Args:
            username (str): The username of the new user.
            full_name (str): The full name of the new user.
            homedir (str): The home directory of the new user.
            shell (str): The default shell of the new user.
            password (str, optional): The password of the new user. Defaults to an empty string.

        Returns:
            dict: A dictionary with status and message.
        """
        try:
            command = f"useradd -m -s {shell} -c {full_name} -d {homedir} {username}"
            output, error, status = await execute(command)
            if status == 0:
                return {
                    "status": 200,
                    "message": f"Utilisateur {username}: full_name: {full_name}, homedir: {homedir}, shell: {shell} créé avec succès !",
                    "stdout": output,
                    "error": error
                }
            else:
                return {
                    "status": 500,
                    "message": f"L'utilisateur {username}: full_name: {full_name}, homedir: {homedir}, shell: {shell} n'a pas été créé",
                    "stdout": output,
                    "error": error
                }
        except Exception as e:
            return {"status": 501, "message": str(e)}

    async def del_user(self, username: str) -> dict:
        """Delete a user from the system.

        Args:
            username (str): The username of the user to delete.

        Returns:
            dict: A dictionary with status and message.
        """
        try:
            command = f"userdel {username}"
            output, error, status = await execute(command)
            if status == 0:
                return {
                    "status": 200,
                    "message": f"Utilisateur {username} a été supprimé avec succès !",
                    "stdout": output,
                    "error": error
                }
            else:
                return {
                    "status": 500,
                    "message": f"Utilisateur {username} n'a pas été supprimé !",
                    "stdout": output,
                    "error": error
                }
        except Exception as e:
            return {"status": 501, "message": str(e)}

    @staticmethod
    def is_login(username: str) -> bool:
        """
        Check if a user is logged in.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the user is logged in, False otherwise.
        """
        all_processes = psutil.process_iter(attrs=['username'])

        for process in all_processes:
            try:
                if process.info['username'] == username:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return False

        return False

    @staticmethod
    async def assign_password(username: str, passwd: str) -> dict:
        """
        Assign a password to a user.

        Args:
            username (str): The username of the user.
            passwd (str): The password of the user.

        Returns:
            dict: A dictionary with status and message.
        """
        try:
            command = f"echo '{passwd}' | sudo passwd --stdin {username}"
            output, error, status = await execute(command)
            if status == 0:
                return {
                    "status": 200,
                    "message": "Le mot de passe a été modifié avec succès",
                    "stdout": output,
                    "error": error
                }
            else:
                return {
                    "status": 500,
                    "message": "Le mot de passe n'a pas été modifié avec succès !",
                    "stdout": output,
                    "error": error
                }
        except Exception as e:
            return {"status": 501, "message": str(e)}

    @staticmethod
    async def update_user(username: str, full_name: str, passwd: str, homedir: str, shell: str) -> dict:
        """
        Update user information.

        Args:
            username (str): The username of the user to update.
            full_name (str): The new full name of the user.
            passwd (str): The new password of the user.
            homedir (str): The new home directory of the user.
            shell (str): The new shell of the user.

        Returns:
            dict: A dictionary with status and message.
        """
        try:
            command = f"usermod -c '{full_name}'"
            if passwd:
                await Users.assign_password(username, passwd)
            if homedir:
                command += f" -d '{homedir}'"
            if shell:
                command += f" -s '{shell}'"
            command += f" {username}"

            # Execute the command
            output, error, status = await execute(command)

            # Check if the command was successful
            if status == 0:
                return {
                    "status": 200,
                    "message": f"User {username} information updated successfully.",
                    "stdout": output,
                    "error": error
                }
            else:
                return {
                    "status": 500,
                    "message": f"Failed to update user {username} information.",
                    "stdout": output,
                    "error": error
                }
        except Exception as e:
            return {"status": 501, "message": str(e)}


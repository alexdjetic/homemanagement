########################################################
# Author: Djetic Alexandre                             
# Description: ce module contient tout le code backend
#              de la gestion du système 
########################################################

import subprocess
import asyncio
import sys


async def execute(cmd: str, timeout: int = 15) -> tuple:
    """
    Execute a command asynchronously and return its output, error, and status.

    Args:
        cmd (str): The command to execute.
        timeout (int): Timeout in seconds (default is 15 seconds).

    Returns:
        tuple: A tuple containing the stdout, stderr, and status code of the command.
    """
    try:
        process = await asyncio.create_subprocess_shell(cmd.replace("^", " "), 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        return stdout.decode().strip(), stderr.decode().strip(), process.returncode
    except asyncio.TimeoutError:
        return "", "Command execution timed out", -1
    except subprocess.CalledProcessError as e:
        return "", str(e), e.returncode
    except Exception as e:
        return "", str(e), -1


async def exec_powershell(cmd: str, timeout: int = 15) -> tuple:
    """
    Execute a PowerShell command asynchronously and return its output, error, and status.

    Args:
        cmd (str): The PowerShell command to execute.
        timeout (int): Timeout in seconds (default is 15 seconds).

    Returns:
        tuple: A tuple containing the stdout, stderr, and status code of the command.
    """
    try:
        process = await asyncio.create_subprocess_shell(
            f"powershell -Command \"{cmd}\"",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        return stdout.strip().decode(), stderr.strip().decode(), process.returncode
    except asyncio.TimeoutError:
        return "", "Command execution timed out", -1
    except subprocess.CalledProcessError as e:
        return "", str(e), e.returncode
    except OSError as e:
        return "", str(e), -1


def get_os() -> str:
    """
    Get the name of the operating system.

    Returns:
        str: The name of the operating system.
    """
    if sys.platform.startswith('win'):
        return "Windows"
    elif sys.platform.startswith('linux'):
        return "Linux"
    elif sys.platform.startswith('darwin'):
        return "macOS"
    else:
        return "Unknown"


if __name__ == "__main__":
    print(f"Operating System: {get_os()}")


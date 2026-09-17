import logging
import platform
import socket
from collections.abc import Iterator

import psutil

from maya_mcp_server.types import MayaListeningPort


logger = logging.getLogger(__name__)


def is_loopback_host(host: str) -> bool:
    """True when host is a loopback address (127.0.0.0/8, ::1, localhost)."""
    if host in ("localhost", "localhost.localdomain"):
        return True
    try:
        import ipaddress

        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def get_platform() -> str:
    """Get normalized platform name."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    return system


def get_maya_process_names() -> list[str]:
    """Get Maya process names for current platform.

    Returns:
        List of possible Maya process names.
    """
    system = get_platform()
    if system == "windows":
        return ["Maya", "maya", "maya.exe", "Maya.exe"]
    elif system == "linux":
        return ["maya", "Maya", "MayaBin", "maya-bin"]
    elif system == "macos":
        return ["Maya", "maya"]
    return ["maya", "Maya"]


def get_maya_process() -> Iterator[psutil.Process]:
    """
    Find all Maya processes.

    Yields:
        Maya Process objects
    """
    valid_names = get_maya_process_names()
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            name = proc.info["name"]
            if name in valid_names:
                yield proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


def get_maya_listening_ports() -> Iterator[MayaListeningPort]:
    """
    Get all ports that Maya processes are listening on.

    Yields:
        MayaListeningPort dictionaries with port, address, and process_id
    """
    found_any_maya = False

    for maya_proc in get_maya_process():
        found_any_maya = True
        logger.debug(f"Found Maya process: PID {maya_proc.pid}")

        try:
            # Get all network connections for Maya process
            connections = maya_proc.net_connections(kind="inet")

            for conn in connections:
                # Only get listening TCP connections on IPv4 (command ports are always IPv4)
                if (
                    conn.status == "LISTEN"
                    and conn.type == socket.SOCK_STREAM
                    and conn.family == socket.AF_INET
                ):
                    yield MayaListeningPort(
                        port=conn.laddr.port,
                        address=conn.laddr.ip,
                        process_id=maya_proc.pid,
                    )

        except psutil.AccessDenied:
            logger.warning(
                f"Access denied getting Maya connections for PID {maya_proc.pid} - "
                "try running as administrator/sudo"
            )
            continue
        except psutil.NoSuchProcess:
            logger.debug(f"Maya process {maya_proc.pid} disappeared during scan")
            continue

    if not found_any_maya:
        logger.debug("Maya is not running")

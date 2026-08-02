import ctypes
import os
import platform
import subprocess
import sys
import winreg
from typing import Dict, List, Optional, Tuple, Any
import psutil

def is_admin() -> bool:
    """Check if the current process is running with Administrator privileges on Windows."""
    if sys.platform != "win32":
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def get_win32_uptime() -> float:
    """Get system uptime in seconds using Win32 API GetTickCount64."""
    try:
        if sys.platform == "win32":
            kernel32 = ctypes.windll.kernel32
            return kernel32.GetTickCount64() / 1000.0
    except Exception:
        pass
    return psutil.boot_time()

def get_system_summary() -> Dict[str, Any]:
    """Retrieve detailed hardware and Windows OS metrics."""
    os_name = f"Windows {platform.release()} ({platform.version()})"
    arch = platform.architecture()[0]
    hostname = platform.node()

    cpu_count_logical = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)
    cpu_usage = psutil.cpu_percent(interval=0.1)

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(os.getcwd()[:3] if sys.platform == "win32" else "/")

    return {
        "os": os_name,
        "arch": arch,
        "hostname": hostname,
        "admin": is_admin(),
        "cpu_cores": f"{cpu_count_physical} Physical / {cpu_count_logical} Logical",
        "cpu_usage": f"{cpu_usage}%",
        "mem_total_gb": round(mem.total / (1024 ** 3), 2),
        "mem_used_gb": round(mem.used / (1024 ** 3), 2),
        "mem_percent": f"{mem.percent}%",
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        "disk_percent": f"{disk.percent}%",
        "uptime_hours": round(get_win32_uptime() / 3600, 2),
    }

def get_git_branch(path: str = ".") -> Optional[str]:
    """Extract active git branch name if path is inside a git working tree."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=1,
        )
        if res.returncode == 0:
            branch = res.stdout.strip()
            if branch:
                return branch
    except Exception:
        pass
    return None

def query_registry_key(hive_str: str, key_path: str) -> List[Tuple[str, Any, str]]:
    """
    Query values inside a Windows Registry Key.
    hives: HKCU (HKEY_CURRENT_USER), HKLM (HKEY_LOCAL_MACHINE), HKCR, HKU
    Returns list of tuples: (name, value, value_type_str)
    """
    hives = {
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
        "HKCR": winreg.HKEY_CLASSES_ROOT,
        "HKU": winreg.HKEY_USERS,
    }
    hive_key = hives.get(hive_str.upper())
    if not hive_key:
        raise ValueError(f"Unknown registry hive '{hive_str}'. Valid hives: {list(hives.keys())}")

    results = []
    try:
        with winreg.OpenKey(hive_key, key_path, 0, winreg.KEY_READ) as key:
            index = 0
            while True:
                try:
                    name, val, val_type = winreg.EnumValue(key, index)
                    type_str = {
                        winreg.REG_SZ: "REG_SZ",
                        winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ",
                        winreg.REG_DWORD: "REG_DWORD",
                        winreg.REG_QWORD: "REG_QWORD",
                        winreg.REG_MULTI_SZ: "REG_MULTI_SZ",
                        winreg.REG_BINARY: "REG_BINARY",
                    }.get(val_type, f"TYPE_{val_type}")
                    results.append((name if name else "(Default)", val, type_str))
                    index += 1
                except OSError:
                    break
    except FileNotFoundError:
        raise FileNotFoundError(f"Registry path not found: {hive_str}\\{key_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied accessing: {hive_str}\\{key_path}")

    return results

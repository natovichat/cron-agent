"""
Factory function for creating OS-specific schedulers.

Automatically detects the operating system and returns the
appropriate scheduler implementation.
"""

import platform
from pathlib import Path
from .base import BaseScheduler


def create_scheduler(script_path: Path, interval_seconds: int = 300) -> BaseScheduler:
    """
    Factory function to create OS-specific scheduler.
    
    Automatically detects the operating system and returns the
    appropriate scheduler implementation:
    - macOS: LaunchdScheduler (LaunchAgents)
    - Linux: SystemdScheduler (if systemd available) or CronScheduler (fallback)
    - Windows: WindowsTaskScheduler (Task Scheduler)
    
    Args:
        script_path: Path to cron_agent.py
        interval_seconds: Interval in seconds (default: 300 = 5 minutes)
        
    Returns:
        OS-specific scheduler instance
        
    Raises:
        OSError: If operating system is not supported
        
    Example:
        >>> scheduler = create_scheduler(Path("cron_agent.py"), interval_seconds=300)
        >>> scheduler.install()
        >>> scheduler.start()
    """
    os_name = platform.system()
    
    if os_name == "Darwin":  # macOS
        from .launchd import LaunchdScheduler
        return LaunchdScheduler(script_path, interval_seconds)
    
    elif os_name == "Linux":
        # Prefer systemd if available
        if _has_systemd():
            from .systemd import SystemdScheduler
            return SystemdScheduler(script_path, interval_seconds)
        else:
            from .cron import CronScheduler
            return CronScheduler(script_path, interval_seconds)
    
    elif os_name == "Windows":
        from .windows_task import WindowsTaskScheduler
        return WindowsTaskScheduler(script_path, interval_seconds)
    
    else:
        raise OSError(f"Unsupported operating system: {os_name}")


def _has_systemd() -> bool:
    """
    Check if systemd is available on the system.
    
    Returns:
        True if systemd is available, False otherwise
    """
    # Check if systemd directory exists
    systemd_path = Path("/run/systemd/system")
    return systemd_path.exists()


def get_scheduler_type() -> str:
    """
    Get the type of scheduler that would be used on this system.
    
    Returns:
        String describing the scheduler type:
        - "launchd" (macOS)
        - "systemd" (Linux with systemd)
        - "cron" (Linux without systemd)
        - "taskschd" (Windows)
        
    Example:
        >>> get_scheduler_type()
        'launchd'
    """
    os_name = platform.system()
    
    if os_name == "Darwin":
        return "launchd"
    elif os_name == "Linux":
        return "systemd" if _has_systemd() else "cron"
    elif os_name == "Windows":
        return "taskschd"
    else:
        return "unknown"

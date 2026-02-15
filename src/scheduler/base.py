"""
Base scheduler abstract class.

Defines the interface that all OS-specific schedulers must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class BaseScheduler(ABC):
    """
    Abstract base class for OS-specific schedulers.
    
    All scheduler implementations must inherit from this class and
    implement the required abstract methods.
    
    Attributes:
        script_path: Path to the cron_agent.py script
        interval_seconds: How often to run the agent in seconds (default: 300 = 5 minutes)
        interval_minutes: Interval in minutes (for schedulers that need it)
    """
    
    def __init__(self, script_path: Path, interval_seconds: int = 300):
        """
        Initialize scheduler.
        
        Args:
            script_path: Absolute path to cron_agent.py (in src/)
            interval_seconds: Interval between runs in seconds
        """
        self.script_path = script_path.resolve()
        self.interval_seconds = interval_seconds
        self.interval_minutes = max(1, interval_seconds // 60)  # For minute-based schedulers
        # script_path is in src/, so project root is one level up
        self.src_dir = self.script_path.parent
        self.project_root = self.src_dir.parent
        self.venv_path = self.src_dir / "venv"
    
    @abstractmethod
    def install(self) -> bool:
        """
        Install scheduler configuration.
        
        Creates the necessary configuration files and registers
        the scheduler with the operating system.
        
        Returns:
            True if installation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def uninstall(self) -> bool:
        """
        Remove scheduler configuration.
        
        Stops the scheduler and removes all configuration files.
        
        Returns:
            True if uninstallation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_installed(self) -> bool:
        """
        Check if scheduler is installed.
        
        Returns:
            True if scheduler configuration exists, False otherwise
        """
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start/enable the scheduler.
        
        Activates the scheduler so it begins running according
        to the configured interval.
        
        Returns:
            True if started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        Stop/disable the scheduler.
        
        Deactivates the scheduler but keeps configuration intact.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def status(self) -> Dict[str, any]:
        """
        Get scheduler status information.
        
        Returns:
            Dictionary with status information including:
            - installed: bool
            - running: bool
            - output: str (additional info)
        """
        pass
    
    def get_python_path(self) -> Path:
        """
        Get path to Python executable in virtual environment.
        
        Returns:
            Path to Python executable
        """
        import platform
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python3"
    
    def ensure_log_dirs(self) -> None:
        """Create log directories if they don't exist."""
        (self.project_root / "logs").mkdir(exist_ok=True)
        (self.project_root / "clean_logs").mkdir(exist_ok=True)

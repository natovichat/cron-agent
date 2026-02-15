"""
Windows Task Scheduler implementation.

Uses Windows Task Scheduler (schtasks.exe) for scheduling on Windows.
"""

import subprocess
import os
from pathlib import Path
from typing import Dict
from .base import BaseScheduler


class WindowsTaskScheduler(BaseScheduler):
    """
    Windows Task Scheduler implementation.
    
    Uses schtasks.exe to create scheduled tasks. Tasks run in user context
    and may require administrator privileges depending on Windows configuration.
    
    Example:
        >>> scheduler = WindowsTaskScheduler(Path("cron_agent.py"), interval_minutes=5)
        >>> scheduler.install()
        >>> scheduler.start()
    """
    
    def __init__(self, script_path: Path, interval_minutes: int = 5):
        """
        Initialize Windows Task Scheduler.
        
        Args:
            script_path: Path to cron_agent.py
            interval_minutes: Interval between runs
        """
        super().__init__(script_path, interval_minutes)
        self.task_name = "CursorCronAgent"
    
    def install(self) -> bool:
        """
        Create Windows scheduled task.
        
        Uses schtasks.exe to create a task that runs every N minutes.
        
        Returns:
            True if task created successfully
        """
        # Ensure log directories exist
        self.ensure_log_dirs()
        
        # Get Python executable path
        python_path = self.get_python_path()
        
        # Build command
        # Use quotes to handle spaces in paths
        command = f'"{python_path}" "{self.script_path}"'
        
        # Create task using schtasks
        try:
            cmd = [
                "schtasks.exe", "/Create",
                "/TN", self.task_name,
                "/TR", command,
                "/SC", "MINUTE",
                "/MO", str(self.interval_minutes),
                "/F"  # Force overwrite if exists
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Windows Task created: {self.task_name}")
                print(f"   Runs every {self.interval_minutes} minutes")
                return True
            else:
                print(f"❌ Failed to create task")
                print(f"   Error: {result.stderr}")
                if "access is denied" in result.stderr.lower():
                    print("   Try running as Administrator")
                return False
                
        except Exception as e:
            print(f"❌ Error creating task: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start/run the scheduled task.
        
        Tasks are enabled by default when created, but this
        can be used to manually trigger a run.
        
        Returns:
            True if started successfully
        """
        if not self.is_installed():
            print("❌ Task not installed. Run install() first.")
            return False
        
        try:
            result = subprocess.run(
                ["schtasks.exe", "/Run", "/TN", self.task_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Task started manually")
                return True
            else:
                print(f"⚠️  Could not start task: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting task: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop/end the running task.
        
        Note: This stops the currently running instance,
        but the task remains scheduled.
        
        Returns:
            True if stopped successfully
        """
        try:
            result = subprocess.run(
                ["schtasks.exe", "/End", "/TN", self.task_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Task stopped")
                return True
            else:
                # Not an error if task wasn't running
                print("⚠️  Task may not be running")
                return True
                
        except Exception as e:
            print(f"❌ Error stopping task: {e}")
            return False
    
    def is_installed(self) -> bool:
        """
        Check if task exists.
        
        Returns:
            True if task exists in Task Scheduler
        """
        try:
            result = subprocess.run(
                ["schtasks.exe", "/Query", "/TN", self.task_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def status(self) -> Dict[str, any]:
        """
        Get task status.
        
        Returns:
            Dictionary with status information
        """
        installed = self.is_installed()
        
        status_dict = {
            "installed": installed,
            "task_name": self.task_name if installed else None,
        }
        
        if installed:
            try:
                # Get detailed info
                result = subprocess.run(
                    ["schtasks.exe", "/Query", "/TN", self.task_name, "/V", "/FO", "LIST"],
                    capture_output=True,
                    text=True
                )
                status_dict["output"] = result.stdout
                
                # Parse to check if running
                if "Running" in result.stdout:
                    status_dict["running"] = True
                elif "Ready" in result.stdout:
                    status_dict["running"] = False
                else:
                    status_dict["running"] = None
                    
            except Exception as e:
                status_dict["output"] = f"Error getting status: {e}"
                status_dict["running"] = None
        else:
            status_dict["output"] = "Not installed"
            status_dict["running"] = False
        
        return status_dict
    
    def uninstall(self) -> bool:
        """
        Delete the scheduled task completely.
        
        Returns:
            True if deleted successfully
        """
        if not self.is_installed():
            print("⚠️  Task not found")
            return True
        
        try:
            result = subprocess.run(
                ["schtasks.exe", "/Delete", "/TN", self.task_name, "/F"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Task deleted: {self.task_name}")
                return True
            else:
                print(f"❌ Failed to delete task: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting task: {e}")
            return False

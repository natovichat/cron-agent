"""
Linux cron scheduler implementation.

Fallback scheduler for Linux systems without systemd.
Uses traditional cron for universal compatibility.
"""

import subprocess
from pathlib import Path
from typing import Dict, List
from .base import BaseScheduler


class CronScheduler(BaseScheduler):
    """
    Linux cron scheduler.
    
    Uses user crontab for scheduling (no sudo required).
    Fallback option for systems without systemd.
    
    Example:
        >>> scheduler = CronScheduler(Path("cron_agent.py"), interval_minutes=5)
        >>> scheduler.install()
        >>> scheduler.start()
    """
    
    def __init__(self, script_path: Path, interval_minutes: int = 5):
        """
        Initialize cron scheduler.
        
        Args:
            script_path: Path to cron_agent.py
            interval_minutes: Interval between runs
        """
        super().__init__(script_path, interval_minutes)
        self.cron_comment = "# Cursor Cron Agent"
    
    def _get_crontab(self) -> List[str]:
        """
        Get current crontab entries.
        
        Returns:
            List of crontab lines
        """
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n') if result.stdout.strip() else []
            return []
        except Exception:
            return []
    
    def _set_crontab(self, lines: List[str]) -> bool:
        """
        Set crontab entries.
        
        Args:
            lines: List of crontab lines
            
        Returns:
            True if successful
        """
        try:
            crontab_content = '\n'.join(lines) + '\n'
            result = subprocess.run(
                ["crontab", "-"],
                input=crontab_content,
                text=True,
                capture_output=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error setting crontab: {e}")
            return False
    
    def _get_cron_expression(self) -> str:
        """
        Generate cron expression for the interval.
        
        Returns:
            Cron time expression (e.g., "*/5 * * * *" for every 5 minutes)
        """
        return f"*/{self.interval_minutes} * * * *"
    
    def _get_cron_command(self) -> str:
        """
        Generate the command to run.
        
        Returns:
            Full command string for crontab
        """
        python_path = self.get_python_path()
        log_file = self.project_root / "logs" / "cron.log"
        
        return f"cd {self.project_root} && {python_path} {self.script_path} --once >> {log_file} 2>&1"
    
    def install(self) -> bool:
        """
        Add cron entry to user crontab.
        
        Returns:
            True if entry added successfully
        """
        # Ensure log directories exist
        self.ensure_log_dirs()
        
        # Get current crontab
        lines = self._get_crontab()
        
        # Check if entry already exists
        if self.is_installed():
            print("⚠️  Cron entry already exists, updating...")
            # Remove old entry
            lines = [line for line in lines if self.cron_comment not in line]
        
        # Add new entry
        cron_expression = self._get_cron_expression()
        cron_command = self._get_cron_command()
        
        lines.append(self.cron_comment)
        lines.append(f"{cron_expression} {cron_command}")
        
        # Set crontab
        if self._set_crontab(lines):
            print(f"✅ Cron entry added")
            print(f"   Runs every {self.interval_minutes} minutes")
            return True
        else:
            print(f"❌ Failed to add cron entry")
            return False
    
    def start(self) -> bool:
        """
        Start cron (actually just checks if installed).
        
        Cron entries are active as soon as they're added,
        so this just verifies the entry exists.
        
        Returns:
            True if entry exists
        """
        if not self.is_installed():
            print("❌ Cron entry not installed. Run install() first.")
            return False
        
        print("✅ Cron entry is active")
        print(f"   Runs every {self.interval_minutes} minutes")
        return True
    
    def stop(self) -> bool:
        """
        Stop cron (removes entry).
        
        Since cron entries are always active, stopping
        means removing the entry.
        
        Returns:
            True if successful
        """
        return self.uninstall()
    
    def is_installed(self) -> bool:
        """
        Check if cron entry exists.
        
        Returns:
            True if entry exists in crontab
        """
        lines = self._get_crontab()
        return any(self.cron_comment in line for line in lines)
    
    def status(self) -> Dict[str, any]:
        """
        Get cron entry status.
        
        Returns:
            Dictionary with status information
        """
        installed = self.is_installed()
        
        status_dict = {
            "installed": installed,
            "running": installed,  # Cron entries are always running if installed
        }
        
        if installed:
            lines = self._get_crontab()
            # Find the cron entry
            for i, line in enumerate(lines):
                if self.cron_comment in line and i + 1 < len(lines):
                    status_dict["output"] = lines[i + 1]
                    break
        else:
            status_dict["output"] = "Not installed"
        
        return status_dict
    
    def uninstall(self) -> bool:
        """
        Remove cron entry from crontab.
        
        Returns:
            True if removed successfully
        """
        if not self.is_installed():
            print("⚠️  Cron entry not found")
            return True
        
        # Get current crontab
        lines = self._get_crontab()
        
        # Remove entry (comment + command line)
        new_lines = []
        skip_next = False
        for line in lines:
            if skip_next:
                skip_next = False
                continue
            if self.cron_comment in line:
                skip_next = True
                continue
            new_lines.append(line)
        
        # Set new crontab
        if self._set_crontab(new_lines):
            print("✅ Cron entry removed")
            return True
        else:
            print("❌ Failed to remove cron entry")
            return False

"""
Linux systemd timer scheduler implementation.

Uses systemd user timers for modern Linux distributions.
Systemd timers are more reliable than cron and provide better logging.
"""

import subprocess
from pathlib import Path
from typing import Dict
from .base import BaseScheduler


class SystemdScheduler(BaseScheduler):
    """
    Linux systemd timer scheduler.
    
    Creates systemd user service and timer units for reliable scheduling.
    Works on modern Linux distros (Ubuntu 16+, Fedora, Debian 8+, etc.).
    
    Files are installed to:
        ~/.config/systemd/user/cronagent.service
        ~/.config/systemd/user/cronagent.timer
    
    Example:
        >>> scheduler = SystemdScheduler(Path("cron_agent.py"), interval_minutes=5)
        >>> scheduler.install()
        >>> scheduler.start()
    """
    
    def __init__(self, script_path: Path, interval_minutes: int = 5):
        """
        Initialize systemd timer scheduler.
        
        Args:
            script_path: Path to cron_agent.py
            interval_minutes: Interval between runs
        """
        super().__init__(script_path, interval_minutes)
        self.service_name = "cronagent"
        self.systemd_dir = Path.home() / ".config" / "systemd" / "user"
        self.service_path = self.systemd_dir / f"{self.service_name}.service"
        self.timer_path = self.systemd_dir / f"{self.service_name}.timer"
    
    def install(self) -> bool:
        """
        Create systemd service and timer files.
        
        Creates both .service and .timer unit files in user systemd directory.
        
        Returns:
            True if files created successfully
        """
        # Ensure log directories exist
        self.ensure_log_dirs()
        
        # Get Python executable path
        python_path = self.get_python_path()
        
        # Create service file content
        service_content = f"""[Unit]
Description=Cursor Cron Agent
After=network.target

[Service]
Type=oneshot
ExecStart={python_path} {self.script_path}
WorkingDirectory={self.project_root}
StandardOutput=append:{self.project_root / "logs" / "stdout.log"}
StandardError=append:{self.project_root / "logs" / "stderr.log"}

[Install]
WantedBy=default.target
"""
        
        # Create timer file content
        timer_content = f"""[Unit]
Description=Cursor Cron Agent Timer
Requires={self.service_name}.service

[Timer]
OnBootSec=1min
OnUnitActiveSec={self.interval_minutes}min
Persistent=true

[Install]
WantedBy=timers.target
"""
        
        try:
            # Ensure systemd user directory exists
            self.systemd_dir.mkdir(parents=True, exist_ok=True)
            
            # Write service file
            self.service_path.write_text(service_content)
            print(f"✅ Created service file: {self.service_path}")
            
            # Write timer file
            self.timer_path.write_text(timer_content)
            print(f"✅ Created timer file: {self.timer_path}")
            
            # Reload systemd daemon
            subprocess.run(
                ["systemctl", "--user", "daemon-reload"],
                capture_output=True
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create systemd files: {e}")
            return False
    
    def start(self) -> bool:
        """
        Enable and start the systemd timer.
        
        Returns:
            True if started successfully
        """
        if not self.is_installed():
            print("❌ Systemd timer not installed. Run install() first.")
            return False
        
        try:
            # Enable timer (start on boot)
            result1 = subprocess.run(
                ["systemctl", "--user", "enable", f"{self.service_name}.timer"],
                capture_output=True,
                text=True
            )
            
            # Start timer now
            result2 = subprocess.run(
                ["systemctl", "--user", "start", f"{self.service_name}.timer"],
                capture_output=True,
                text=True
            )
            
            if result1.returncode == 0 and result2.returncode == 0:
                print(f"✅ Systemd timer enabled and started")
                print(f"   Runs every {self.interval_minutes} minutes")
                return True
            else:
                print(f"❌ Failed to start timer")
                if result1.stderr:
                    print(f"   Enable error: {result1.stderr}")
                if result2.stderr:
                    print(f"   Start error: {result2.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting systemd timer: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the systemd timer.
        
        Returns:
            True if stopped successfully
        """
        try:
            result = subprocess.run(
                ["systemctl", "--user", "stop", f"{self.service_name}.timer"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Systemd timer stopped")
                return True
            else:
                print(f"⚠️  Timer may not be running: {result.stderr}")
                return True
                
        except Exception as e:
            print(f"❌ Error stopping timer: {e}")
            return False
    
    def is_installed(self) -> bool:
        """
        Check if systemd files exist.
        
        Returns:
            True if both service and timer files exist
        """
        return self.service_path.exists() and self.timer_path.exists()
    
    def is_running(self) -> bool:
        """
        Check if timer is active.
        
        Returns:
            True if timer is running
        """
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", f"{self.service_name}.timer"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() == "active"
        except Exception:
            return False
    
    def status(self) -> Dict[str, any]:
        """
        Get systemd timer status.
        
        Returns:
            Dictionary with status information
        """
        installed = self.is_installed()
        running = self.is_running()
        
        status_dict = {
            "installed": installed,
            "running": running,
            "service_path": str(self.service_path) if installed else None,
            "timer_path": str(self.timer_path) if installed else None,
        }
        
        if installed:
            try:
                result = subprocess.run(
                    ["systemctl", "--user", "status", f"{self.service_name}.timer"],
                    capture_output=True,
                    text=True
                )
                status_dict["output"] = result.stdout
            except Exception as e:
                status_dict["output"] = f"Error getting status: {e}"
        else:
            status_dict["output"] = "Not installed"
        
        return status_dict
    
    def uninstall(self) -> bool:
        """
        Stop and remove systemd timer completely.
        
        Returns:
            True if uninstalled successfully
        """
        success = True
        
        # Stop if running
        if self.is_running():
            subprocess.run(
                ["systemctl", "--user", "stop", f"{self.service_name}.timer"],
                capture_output=True
            )
        
        # Disable
        subprocess.run(
            ["systemctl", "--user", "disable", f"{self.service_name}.timer"],
            capture_output=True
        )
        
        # Remove files
        if self.is_installed():
            try:
                if self.service_path.exists():
                    self.service_path.unlink()
                    print(f"✅ Removed: {self.service_path}")
                
                if self.timer_path.exists():
                    self.timer_path.unlink()
                    print(f"✅ Removed: {self.timer_path}")
                
                # Reload daemon
                subprocess.run(
                    ["systemctl", "--user", "daemon-reload"],
                    capture_output=True
                )
                
            except Exception as e:
                print(f"❌ Failed to remove files: {e}")
                success = False
        
        return success

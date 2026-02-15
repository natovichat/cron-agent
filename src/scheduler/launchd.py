"""
macOS LaunchAgent scheduler implementation.

Uses macOS LaunchAgents for reliable scheduling that survives
sleep/wake cycles.
"""

import subprocess
from pathlib import Path
from typing import Dict
from .base import BaseScheduler


class LaunchdScheduler(BaseScheduler):
    """
    macOS LaunchAgent scheduler.
    
    Creates a LaunchAgent plist file and registers it with launchd.
    LaunchAgents run in user context and don't require sudo.
    
    The plist file is installed to:
        ~/Library/LaunchAgents/com.cursor.cronagent.plist
    
    Example:
        >>> scheduler = LaunchdScheduler(Path("cron_agent.py"), interval_minutes=5)
        >>> scheduler.install()
        >>> scheduler.start()
        >>> print(scheduler.status())
    """
    
    def __init__(self, script_path: Path, interval_minutes: int = 5):
        """
        Initialize macOS LaunchAgent scheduler.
        
        Args:
            script_path: Path to cron_agent.py
            interval_minutes: Interval between runs
        """
        super().__init__(script_path, interval_minutes)
        self.plist_name = "com.cursor.cronagent"
        self.plist_path = Path.home() / "Library" / "LaunchAgents" / f"{self.plist_name}.plist"
    
    def install(self) -> bool:
        """
        Create and install LaunchAgent plist file.
        
        Creates a plist configuration file and writes it to
        ~/Library/LaunchAgents/. Does NOT load the agent yet
        (use start() for that).
        
        Returns:
            True if plist created successfully
        """
        # Ensure log directories exist
        self.ensure_log_dirs()
        
        # Get Python executable path
        python_path = self.get_python_path()
        
        # Create plist content
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{self.plist_name}</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{self.script_path}</string>
    </array>
    
    <key>StartInterval</key>
    <integer>{self.interval_minutes * 60}</integer>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>{self.project_root / "logs" / "stdout.log"}</string>
    
    <key>StandardErrorPath</key>
    <string>{self.project_root / "logs" / "stderr.log"}</string>
    
    <key>WorkingDirectory</key>
    <string>{self.project_root}</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>"""
        
        try:
            # Ensure LaunchAgents directory exists
            self.plist_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write plist file
            self.plist_path.write_text(plist_content)
            
            print(f"✅ LaunchAgent plist created: {self.plist_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create plist: {e}")
            return False
    
    def start(self) -> bool:
        """
        Load and start the LaunchAgent.
        
        Uses launchctl to load the agent, which starts it immediately
        and schedules it to run at the configured interval.
        
        Returns:
            True if loaded successfully
        """
        if not self.is_installed():
            print("❌ LaunchAgent not installed. Run install() first.")
            return False
        
        try:
            # Unload first if already loaded (to reload config)
            subprocess.run(
                ["launchctl", "unload", str(self.plist_path)],
                capture_output=True,
                check=False  # Don't fail if not loaded
            )
            
            # Load the agent
            result = subprocess.run(
                ["launchctl", "load", str(self.plist_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ LaunchAgent loaded and started")
                print(f"   Runs every {self.interval_minutes} minutes")
                return True
            else:
                print(f"❌ Failed to load LaunchAgent: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting LaunchAgent: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Unload the LaunchAgent.
        
        Stops the agent from running but keeps the plist file.
        Use start() to reload it.
        
        Returns:
            True if unloaded successfully
        """
        try:
            result = subprocess.run(
                ["launchctl", "unload", str(self.plist_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ LaunchAgent stopped")
                return True
            else:
                print(f"⚠️  LaunchAgent may not be running: {result.stderr}")
                return True  # Not an error if it wasn't running
                
        except Exception as e:
            print(f"❌ Error stopping LaunchAgent: {e}")
            return False
    
    def is_installed(self) -> bool:
        """
        Check if plist file exists.
        
        Returns:
            True if plist file exists
        """
        return self.plist_path.exists()
    
    def is_running(self) -> bool:
        """
        Check if LaunchAgent is currently loaded.
        
        Returns:
            True if agent is loaded and running
        """
        try:
            result = subprocess.run(
                ["launchctl", "list", self.plist_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def status(self) -> Dict[str, any]:
        """
        Get LaunchAgent status.
        
        Returns:
            Dictionary with status information:
            - installed: bool - plist file exists
            - running: bool - agent is loaded
            - plist_path: str - path to plist file
            - output: str - launchctl list output
        """
        installed = self.is_installed()
        running = self.is_running()
        
        status_dict = {
            "installed": installed,
            "running": running,
            "plist_path": str(self.plist_path) if installed else None,
        }
        
        if running:
            try:
                result = subprocess.run(
                    ["launchctl", "list", self.plist_name],
                    capture_output=True,
                    text=True
                )
                status_dict["output"] = result.stdout
            except Exception as e:
                status_dict["output"] = f"Error getting details: {e}"
        else:
            status_dict["output"] = "Not running"
        
        return status_dict
    
    def uninstall(self) -> bool:
        """
        Stop and remove LaunchAgent completely.
        
        Unloads the agent and deletes the plist file.
        
        Returns:
            True if uninstalled successfully
        """
        success = True
        
        # Stop if running
        if self.is_running():
            if not self.stop():
                success = False
        
        # Remove plist file
        if self.is_installed():
            try:
                self.plist_path.unlink()
                print(f"✅ Removed plist file: {self.plist_path}")
            except Exception as e:
                print(f"❌ Failed to remove plist: {e}")
                success = False
        
        return success

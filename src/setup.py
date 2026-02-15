#!/usr/bin/env python3
"""
Cross-platform setup script for Cron Agent.

Works on: macOS, Linux, Windows

Usage:
    python3 setup.py        # macOS/Linux
    python setup.py         # Windows
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @classmethod
    def disable(cls):
        """Disable colors (for Windows without ANSI support)."""
        cls.HEADER = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.GREEN = ''
        cls.WARNING = ''
        cls.FAIL = ''
        cls.ENDC = ''
        cls.BOLD = ''


# Disable colors on Windows unless forced
if platform.system() == "Windows" and not os.environ.get("FORCE_COLOR"):
    Colors.disable()


class SetupManager:
    """
    Cross-platform setup manager.
    
    Handles installation on macOS, Linux, and Windows.
    """
    
    def __init__(self):
        self.os_name = platform.system()
        # Project root is one level up from src/
        self.src_dir = Path(__file__).parent.resolve()
        self.project_root = self.src_dir.parent
        self.venv_path = self.src_dir / "venv"
        
    def run(self):
        """Run the complete setup process."""
        self.print_header()
        self.check_python()
        self.create_venv()
        self.install_dependencies()
        self.setup_env_file()
        self.show_completion()
    
    def print_header(self):
        """Print setup header."""
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}🚀 Cron Agent Setup{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
        print(f"\nOperating System: {Colors.BOLD}{self.os_name}{Colors.ENDC}")
        print()
    
    def check_python(self):
        """Check Python version."""
        print(f"{Colors.BLUE}📋 Checking Python installation...{Colors.ENDC}")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"{Colors.FAIL}❌ Python 3.8+ required!{Colors.ENDC}")
            print(f"   Current version: Python {version_str}")
            print("\nInstall Python 3.8+ from:")
            print("  macOS: brew install python3")
            print("  Ubuntu/Debian: sudo apt install python3 python3-pip")
            print("  Windows: https://www.python.org/downloads/")
            sys.exit(1)
        
        print(f"{Colors.GREEN}✅ Python {version_str} installed{Colors.ENDC}")
        print()
    
    def create_venv(self):
        """Create virtual environment."""
        print(f"{Colors.BLUE}📦 Creating virtual environment...{Colors.ENDC}")
        
        if self.venv_path.exists():
            print(f"{Colors.WARNING}⚠️  Virtual environment already exists{Colors.ENDC}")
            print()
            return
        
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                check=True,
                capture_output=True
            )
            print(f"{Colors.GREEN}✅ Virtual environment created{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ Error creating virtual environment:{Colors.ENDC}")
            print(e.stderr.decode() if e.stderr else str(e))
            sys.exit(1)
        
        print()
    
    def get_pip_path(self) -> Path:
        """Get path to pip executable in venv."""
        if self.os_name == "Windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip3"
    
    def get_python_path(self) -> Path:
        """Get path to Python executable in venv."""
        if self.os_name == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python3"
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print(f"{Colors.BLUE}📥 Installing dependencies...{Colors.ENDC}")
        
        pip = self.get_pip_path()
        requirements = self.src_dir / "requirements.txt"
        
        if not requirements.exists():
            print(f"{Colors.WARNING}⚠️  requirements.txt not found{Colors.ENDC}")
            return
        
        try:
            # Upgrade pip silently
            subprocess.run(
                [str(pip), "install", "--upgrade", "pip"],
                check=True,
                capture_output=True
            )
            
            # Install requirements
            print(f"   Installing packages from requirements.txt...")
            result = subprocess.run(
                [str(pip), "install", "-r", str(requirements)],
                check=True,
                capture_output=True,
                text=True
            )
            
            print(f"{Colors.GREEN}✅ All dependencies installed{Colors.ENDC}")
            
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ Error installing dependencies:{Colors.ENDC}")
            print(e.stderr if e.stderr else str(e))
            sys.exit(1)
        
        print()
    
    def setup_env_file(self):
        """Create .env file and prompt for Todoist token."""
        print(f"{Colors.BLUE}📝 Configuring .env file...{Colors.ENDC}")
        print()
        
        env_file = self.project_root / ".env"
        
        if env_file.exists():
            print(f"{Colors.WARNING}⚠️  .env file already exists{Colors.ENDC}")
            print()
            # Ask if they want to update it
            response = input("Update the Token? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                return
        
        # Prompt for Todoist token
        print(f"{Colors.CYAN}🔑 Todoist API Token{Colors.ENDC}")
        print()
        print("Get your token from:")
        print(f"{Colors.BOLD}https://todoist.com/app/settings/integrations/developer{Colors.ENDC}")
        print()
        
        token = input("Enter your Todoist API token: ").strip()
        
        while not token:
            print(f"{Colors.FAIL}❌ Token cannot be empty!{Colors.ENDC}")
            token = input("Enter your Todoist API token: ").strip()
        
        # Create .env file with token
        env_content = f"""# Cron Agent Configuration
# Auto-generated by setup

TODOIST_TOKEN={token}
"""
        env_file.write_text(env_content)
        print()
        print(f"{Colors.GREEN}✅ .env file created with your token{Colors.ENDC}")
        print()
    
    def show_completion(self):
        """Show completion message and next steps."""
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}✅ Setup completed successfully!{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.ENDC}")
        print()
        
        print(f"{Colors.BOLD}📋 Next Steps:{Colors.ENDC}")
        print()
        
        # Step 1: Install scheduler
        print(f"{Colors.CYAN}1. Install scheduler:{Colors.ENDC}")
        print(f"   ./cronagent install")
        print()
        
        # Step 2: Verify
        print(f"{Colors.CYAN}2. Check status:{Colors.ENDC}")
        print(f"   ./cronagent status")
        print()
        
        # OS-specific notes
        if self.os_name == "Darwin":
            print(f"{Colors.BLUE}ℹ️  macOS Notes:{Colors.ENDC}")
            print(f"   - Will install LaunchAgent in ~/Library/LaunchAgents/")
            print(f"   - No sudo required")
            print(f"   - Runs automatically on login")
        elif self.os_name == "Linux":
            print(f"{Colors.BLUE}ℹ️  Linux Notes:{Colors.ENDC}")
            print(f"   - If systemd available: uses systemd timer")
            print(f"   - Otherwise: uses cron")
            print(f"   - No sudo required (user-level)")
        elif self.os_name == "Windows":
            print(f"{Colors.BLUE}ℹ️  Windows Notes:{Colors.ENDC}")
            print(f"   - Uses Task Scheduler")
            print(f"   - May need \"Run as Administrator\"")
            print(f"   - Can manage via Task Scheduler GUI")
        
        print()
        print(f"{Colors.BOLD}📚 More Info:{Colors.ENDC}")
        print(f"   - README: cat docs/README.md")
        print(f"   - Setup guide: docs/setup-guide.html")
        print()
        print(f"{Colors.BOLD}{Colors.GREEN}🎉 Success!{Colors.ENDC}")


def main():
    """Main entry point."""
    try:
        setup = SetupManager()
        setup.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Unexpected error:{Colors.ENDC}")
        print(str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

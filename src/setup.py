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
        print(f"{Colors.BLUE}📋 בודק התקנת Python...{Colors.ENDC}")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"{Colors.FAIL}❌ Python 3.8+ נדרש!{Colors.ENDC}")
            print(f"   גרסה נוכחית: Python {version_str}")
            print("\nהתקן Python 3.8+ מ:")
            print("  macOS: brew install python3")
            print("  Ubuntu/Debian: sudo apt install python3 python3-pip")
            print("  Windows: https://www.python.org/downloads/")
            sys.exit(1)
        
        print(f"{Colors.GREEN}✅ Python {version_str} מותקן{Colors.ENDC}")
        print()
    
    def create_venv(self):
        """Create virtual environment."""
        print(f"{Colors.BLUE}📦 יוצר virtual environment...{Colors.ENDC}")
        
        if self.venv_path.exists():
            print(f"{Colors.WARNING}⚠️  Virtual environment כבר קיים{Colors.ENDC}")
            print()
            return
        
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)],
                check=True,
                capture_output=True
            )
            print(f"{Colors.GREEN}✅ Virtual environment נוצר{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ שגיאה ביצירת virtual environment:{Colors.ENDC}")
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
        print(f"{Colors.BLUE}📥 מתקין תלויות...{Colors.ENDC}")
        
        pip = self.get_pip_path()
        requirements = self.src_dir / "requirements.txt"
        
        if not requirements.exists():
            print(f"{Colors.WARNING}⚠️  requirements.txt לא נמצא{Colors.ENDC}")
            return
        
        try:
            # Upgrade pip silently
            subprocess.run(
                [str(pip), "install", "--upgrade", "pip"],
                check=True,
                capture_output=True
            )
            
            # Install requirements
            print(f"   מתקין packages מ-requirements.txt...")
            result = subprocess.run(
                [str(pip), "install", "-r", str(requirements)],
                check=True,
                capture_output=True,
                text=True
            )
            
            print(f"{Colors.GREEN}✅ כל התלויות הותקנו{Colors.ENDC}")
            
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ שגיאה בהתקנת תלויות:{Colors.ENDC}")
            print(e.stderr if e.stderr else str(e))
            sys.exit(1)
        
        print()
    
    def setup_env_file(self):
        """Create .env file from template."""
        print(f"{Colors.BLUE}📝 מגדיר קובץ .env...{Colors.ENDC}")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists():
            print(f"{Colors.WARNING}⚠️  קובץ .env כבר קיים{Colors.ENDC}")
            print()
            return
        
        if not env_example.exists():
            print(f"{Colors.WARNING}⚠️  .env.example לא נמצא, יוצר .env ריק{Colors.ENDC}")
            env_file.write_text("# Cron Agent Configuration\nTODOIST_TOKEN=\n")
        else:
            env_file.write_text(env_example.read_text())
            print(f"{Colors.GREEN}✅ קובץ .env נוצר מ-.env.example{Colors.ENDC}")
        
        print(f"\n{Colors.WARNING}⚠️  חשוב! ערוך את .env והוסף את ה-TODOIST_TOKEN שלך{Colors.ENDC}")
        print(f"   קבל Token מ: https://todoist.com/app/settings/integrations/developer")
        print()
    
    def show_completion(self):
        """Show completion message and next steps."""
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}✅ ההתקנה הושלמה בהצלחה!{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.ENDC}")
        print()
        
        print(f"{Colors.BOLD}📋 צעדים הבאים:{Colors.ENDC}")
        print()
        
        # Step 1: Configure token
        print(f"{Colors.CYAN}1. הגדר את Todoist Token:{Colors.ENDC}")
        print(f"   - ערוך את קובץ .env (ברמה הראשית של הפרויקט)")
        print(f"   - הוסף: TODOIST_TOKEN=your-token-here")
        print(f"   - קבל Token מ: https://todoist.com/app/settings/integrations/developer")
        print()
        
        # Step 2: (Optional) Adjust config
        print(f"{Colors.CYAN}2. (אופציונלי) התאם הגדרות ב-config.json:{Colors.ENDC}")
        print(f"   - polling_interval_minutes: {Colors.BOLD}5{Colors.ENDC} (ברירת מחדל)")
        print()
        
        # Step 3: Install scheduler
        print(f"{Colors.CYAN}3. התקן scheduler:{Colors.ENDC}")
        print(f"   ./cronagent --install")
        print()
        
        # Step 4: Verify
        print(f"{Colors.CYAN}4. בדוק status:{Colors.ENDC}")
        print(f"   ./cronagent --status")
        print()
        
        # OS-specific notes
        if self.os_name == "Darwin":
            print(f"{Colors.BLUE}ℹ️  macOS Notes:{Colors.ENDC}")
            print(f"   - יותקן LaunchAgent ב-~/Library/LaunchAgents/")
            print(f"   - לא נדרש sudo")
            print(f"   - ירוץ אוטומטית בכל login")
        elif self.os_name == "Linux":
            print(f"{Colors.BLUE}ℹ️  Linux Notes:{Colors.ENDC}")
            print(f"   - אם יש systemd: ישתמש ב-systemd timer")
            print(f"   - אחרת: ישתמש ב-cron")
            print(f"   - לא נדרש sudo (user-level)")
        elif self.os_name == "Windows":
            print(f"{Colors.BLUE}ℹ️  Windows Notes:{Colors.ENDC}")
            print(f"   - ישתמש ב-Task Scheduler")
            print(f"   - ייתכן שנדרש \"Run as Administrator\"")
            print(f"   - ניתן לנהל דרך Task Scheduler GUI")
        
        print()
        print(f"{Colors.BOLD}📚 למידע נוסף:{Colors.ENDC}")
        print(f"   - README: cat README.md")
        print(f"   - Setup guide: docs/setup-guide.html")
        print()
        print(f"{Colors.BOLD}{Colors.GREEN}🎉 בהצלחה!{Colors.ENDC}")


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

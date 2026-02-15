# 📁 Project File Structure

Complete guide to the Cron Agent project organization.

---

## 📊 Overview

```
cron-agent/
├── 📄 Core Files (Entry Points & Config)
├── 📁 scheduler/ (Scheduler Abstraction Layer)
├── 📁 docs/ (Documentation)
├── 📁 logs/ (Runtime Logs - Auto-generated)
├── 📁 clean_logs/ (Conversation Logs - Auto-generated)
└── 📁 venv/ (Virtual Environment - Auto-generated)
```

---

## 🗂️ Complete Directory Tree

```
cron-agent/
│
├── 📄 cron_agent.py              # Main application & entry point
├── 📄 setup.py                   # Cross-platform setup script
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # Main project documentation
├── 📄 CHANGELOG.md               # Version history
├── 📄 IMPLEMENTATION_SUMMARY.md  # Technical implementation details
│
├── 📄 .env                       # Configuration (NOT committed)
├── 📄 .env.example               # Environment variables template
├── 📄 .gitignore                 # Git ignore rules
│
├── 📁 scheduler/                 # Scheduler abstraction layer
│   ├── __init__.py              # Package initialization
│   ├── base.py                  # Abstract base class
│   ├── factory.py               # OS detection & factory
│   ├── launchd.py               # macOS LaunchAgents
│   ├── systemd.py               # Linux systemd timers
│   ├── cron.py                  # Linux cron fallback
│   └── windows_task.py          # Windows Task Scheduler
│
├── 📁 docs/                      # Documentation
│   ├── README.md                # Documentation index
│   ├── setup-guide.html         # Interactive setup guide
│   └── FILE_STRUCTURE.md        # This file
│
├── 📁 logs/                      # Technical logs (auto-generated)
│   ├── stdout.log               # Standard output
│   └── stderr.log               # Error messages
│
├── 📁 clean_logs/                # Conversation logs (auto-generated)
│   ├── README.md                # Clean logs documentation
│   └── conversation_YYYY-MM-DD.log  # Daily conversation logs
│
├── 📁 venv/                      # Virtual environment (auto-generated)
│   ├── bin/                     # Executables (macOS/Linux)
│   ├── Scripts/                 # Executables (Windows)
│   ├── lib/                     # Python libraries
│   └── ...
│
└── 📁 .git/                      # Git repository (auto-generated)
```

---

## 📄 Core Files

### `cron_agent.py`
**Purpose**: Main application - the heart of the system  
**Size**: ~408 lines  
**Key Components**:
- `CleanLogger` - Clean conversation logging
- `TodoistAPI` - Todoist integration
- `CursorAgent` - AI task execution (simulated)
- `CronAgent` - Main orchestration engine
- CLI argument parsing (--install, --status, --uninstall)

**Usage**:
```bash
# Regular execution (run agent once)
./venv/bin/python cron_agent.py

# Scheduler management
./venv/bin/python cron_agent.py --install
./venv/bin/python cron_agent.py --status
./venv/bin/python cron_agent.py --uninstall
```

**Dependencies**: schedule, requests, python-dotenv

---

### `setup.py`
**Purpose**: Cross-platform setup script  
**Size**: ~348 lines  
**Replaces**: Old `setup.sh` (bash-only)

**Features**:
- ✅ Works on macOS, Linux, Windows
- ✅ Python version check (requires 3.8+)
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Creates .env from template
- ✅ Color-coded output
- ✅ OS-specific instructions

**Usage**:
```bash
python3 setup.py  # macOS/Linux
python setup.py   # Windows
```

---

### `requirements.txt`
**Purpose**: Python package dependencies  
**Format**: pip requirements format

**Contents**:
```
schedule==1.2.0          # Job scheduling
requests==2.31.0         # HTTP/API calls
python-dotenv==1.0.0     # Environment variables
pytest==7.4.0            # Testing (dev)
black==23.7.0            # Formatting (dev)
flake8==6.1.0            # Linting (dev)
```

**Usage**:
```bash
pip install -r requirements.txt
```

---

### `.env` (User Configuration)
**Purpose**: Environment variables and secrets  
**Status**: ⚠️ **NOT committed to git** (in .gitignore)  
**Created**: Automatically by setup.py

**Contents**:
```bash
# Todoist API Configuration
TODOIST_TOKEN=your_token_here

# Optional: Custom log directory
CLEAN_LOGS_DIR=clean_logs
```

**Important**: Always edit this file after setup to add your Todoist token!

---

### `.env.example`
**Purpose**: Template for .env file  
**Status**: ✅ Committed to git  
**Used by**: setup.py to create initial .env

**Contents**: Same structure as .env but with placeholder values

---

## 📁 scheduler/ Directory

The **scheduler abstraction layer** - makes the app cross-platform.

### Architecture Pattern: Factory + Strategy

```
┌─────────────────┐
│  factory.py     │  ← Auto-detects OS
└────────┬────────┘
         │
    ┌────┴─────┬─────────┬──────────┐
    ↓          ↓         ↓          ↓
launchd.py systemd.py cron.py windows_task.py
```

---

### `scheduler/__init__.py`
**Purpose**: Package initialization  
**Size**: ~13 lines  
**Exports**: 
- `create_scheduler()` - Main factory function
- `BaseScheduler` - Abstract base class

**Usage**:
```python
from scheduler import create_scheduler

scheduler = create_scheduler(script_path, interval_minutes=5)
scheduler.install()
scheduler.start()
```

---

### `scheduler/base.py`
**Purpose**: Abstract base class for all schedulers  
**Size**: ~136 lines  
**Pattern**: Abstract Base Class (ABC)

**Defines Interface**:
- `install()` - Install scheduler configuration
- `uninstall()` - Remove scheduler
- `is_installed()` - Check if installed
- `start()` - Start/enable scheduler
- `stop()` - Stop/disable scheduler
- `status()` - Get status info

**Helper Methods**:
- `get_python_path()` - Get venv Python executable
- `ensure_log_dirs()` - Create log directories

**All platform implementations must inherit from this class.**

---

### `scheduler/factory.py`
**Purpose**: OS detection and scheduler creation  
**Size**: ~92 lines  
**Pattern**: Factory Pattern

**Main Function**: `create_scheduler(script_path, interval_minutes)`

**Logic Flow**:
```python
if macOS:
    return LaunchdScheduler()
elif Linux:
    if has_systemd():
        return SystemdScheduler()
    else:
        return CronScheduler()
elif Windows:
    return WindowsTaskScheduler()
```

**Helper Functions**:
- `_has_systemd()` - Check if systemd available
- `get_scheduler_type()` - Return scheduler type name

---

### `scheduler/launchd.py`
**Purpose**: macOS LaunchAgent implementation  
**Size**: ~307 lines  
**Platform**: macOS only

**Features**:
- Creates plist file in `~/Library/LaunchAgents/`
- Uses `launchctl` for management
- No sudo required (user-level)
- Survives sleep/wake cycles

**Plist Location**: `~/Library/LaunchAgents/com.cursor.cronagent.plist`

**Key Methods**:
- `install()` - Creates plist file
- `start()` - Loads with launchctl
- `stop()` - Unloads agent
- `is_running()` - Checks if loaded

**Management Commands**:
```bash
launchctl list | grep cronagent
launchctl load ~/Library/LaunchAgents/com.cursor.cronagent.plist
launchctl unload ~/Library/LaunchAgents/com.cursor.cronagent.plist
```

---

### `scheduler/systemd.py`
**Purpose**: Linux systemd timer implementation  
**Size**: ~286 lines  
**Platform**: Linux (modern distros)

**Features**:
- Creates .service and .timer files
- User-level systemd (no sudo)
- Persistent across reboots
- Built-in logging (journalctl)

**Files Created**:
- `~/.config/systemd/user/cronagent.service`
- `~/.config/systemd/user/cronagent.timer`

**Management Commands**:
```bash
systemctl --user status cronagent.timer
systemctl --user start cronagent.timer
systemctl --user stop cronagent.timer
journalctl --user -u cronagent.service -f
```

---

### `scheduler/cron.py`
**Purpose**: Linux cron implementation (fallback)  
**Size**: ~217 lines  
**Platform**: Linux (universal, any distro)

**Features**:
- Uses user crontab (no sudo)
- Universal Linux compatibility
- Fallback for non-systemd systems

**Crontab Entry Example**:
```cron
# Cursor Cron Agent
*/5 * * * * cd /path/to/project && /path/to/venv/bin/python /path/to/cron_agent.py >> logs/cron.log 2>&1
```

**Management Commands**:
```bash
crontab -l  # List entries
crontab -e  # Edit crontab
```

---

### `scheduler/windows_task.py`
**Purpose**: Windows Task Scheduler implementation  
**Size**: ~237 lines  
**Platform**: Windows

**Features**:
- Uses `schtasks.exe`
- Native Windows integration
- GUI management available
- May require admin privileges

**Task Name**: `CursorCronAgent`

**Management Commands**:
```bash
# CLI
schtasks /Query /TN "CursorCronAgent" /FO LIST
schtasks /Run /TN "CursorCronAgent"
schtasks /Delete /TN "CursorCronAgent" /F

# GUI
Win+R → taskschd.msc
```

---

## 📁 docs/ Directory

Documentation files for the project.

### `docs/README.md`
**Purpose**: Documentation index  
**Size**: ~2,530 bytes  
**Contents**: Overview of documentation files

---

### `docs/setup-guide.html`
**Purpose**: Interactive HTML setup guide  
**Size**: ~1,117 lines  
**Type**: Single-page web application

**Features**:
- 🎨 Beautiful gradient design
- 📱 Fully responsive
- 🔄 Interactive tabs (macOS/Linux/Windows/Comparison)
- 📝 Step-by-step instructions per OS
- 📊 Comparison tables
- 🎯 Copy-paste commands
- ⚠️ Warning/Success/Info boxes

**Tabs**:
1. **macOS**: LaunchAgent setup
2. **Linux**: systemd/cron setup
3. **Windows**: Task Scheduler setup
4. **Comparison**: Side-by-side comparison

**Usage**:
```bash
open docs/setup-guide.html  # macOS
xdg-open docs/setup-guide.html  # Linux
start docs/setup-guide.html  # Windows
```

---

### `docs/FILE_STRUCTURE.md`
**Purpose**: This file - project structure documentation  
**Type**: Reference documentation

---

## 📁 logs/ Directory

**Purpose**: Technical logs (debugging, stdout, stderr)  
**Status**: Auto-generated, not committed to git

### `logs/stdout.log`
**Contains**: Standard output from cron_agent.py
- Execution timestamps
- Task processing info
- Statistics
- Info messages

### `logs/stderr.log`
**Contains**: Error messages and exceptions
- Python tracebacks
- API errors
- Warning messages

**View Logs**:
```bash
tail -f logs/stdout.log
tail -f logs/stderr.log
```

---

## 📁 clean_logs/ Directory

**Purpose**: Conversation logs (prompts + AI responses only)  
**Status**: Auto-generated, not committed to git

### `clean_logs/conversation_YYYY-MM-DD.log`
**Format**: Daily log files
**Contains**: Clean conversation history
- Timestamp
- Task ID
- Prompt sent to AI
- Response from AI
- No debugging info

**Example**:
```
======================================================================
[2025-02-15 14:30:00] Task ID: abc123

📤 PROMPT:
שלח מייל ללקוח עם עדכון הזמנה

📥 RESPONSE:
✉️ נשלח מייל אוטומטי ללקוח

======================================================================
```

**Usage**: Perfect for presentations, documentation, and understanding what the agent did.

**View Logs**:
```bash
./view_clean_logs.sh          # Interactive viewer
python analyze_clean_logs.py  # Statistics
tail -f clean_logs/conversation_$(date +%Y-%m-%d).log
```

---

## 📁 venv/ Directory

**Purpose**: Python virtual environment  
**Status**: Auto-generated by setup.py, not committed to git

**Structure**:
```
venv/
├── bin/          # Executables (macOS/Linux)
│   ├── python    # Python interpreter
│   ├── pip       # Package installer
│   └── activate  # Activation script
├── Scripts/      # Executables (Windows)
│   ├── python.exe
│   ├── pip.exe
│   └── activate.bat
├── lib/          # Installed packages
│   └── python3.X/
│       └── site-packages/
└── pyvenv.cfg    # Configuration
```

**Activate**:
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Use Without Activating**:
```bash
./venv/bin/python cron_agent.py  # macOS/Linux
.\venv\Scripts\python cron_agent.py  # Windows
```

---

## 📊 File Statistics

### By Type:

| Type | Count | Total Lines |
|------|-------|-------------|
| Python (.py) | 8 | ~1,940 |
| Markdown (.md) | 5 | ~1,200 |
| HTML (.html) | 1 | ~1,117 |
| Config (.txt, .env) | 3 | ~88 |
| **Total** | **17** | **~4,345** |

### By Category:

| Category | Files | Lines |
|----------|-------|-------|
| Core Application | 3 | ~756 |
| Scheduler Layer | 7 | ~1,275 |
| Documentation | 5 | ~2,230 |
| Configuration | 2 | ~88 |

---

## 🔍 File Dependencies

### Import Graph:

```
cron_agent.py
    ├── scheduler.factory
    │   └── scheduler.base
    │       ├── scheduler.launchd
    │       ├── scheduler.systemd
    │       ├── scheduler.cron
    │       └── scheduler.windows_task
    ├── schedule (external)
    ├── requests (external)
    └── python-dotenv (external)

setup.py
    └── (no internal dependencies)
```

---

## 🚫 Files NOT in Repository

These files are auto-generated or contain secrets (listed in .gitignore):

```
❌ .env                    # User secrets
❌ venv/                   # Virtual environment
❌ logs/                   # Technical logs
❌ clean_logs/             # Conversation logs
❌ __pycache__/            # Python cache
❌ *.pyc                   # Compiled Python
❌ .DS_Store               # macOS metadata
❌ *.log                   # Log files
```

---

## 📝 File Naming Conventions

### Python Files:
- `snake_case.py` - All Python files
- `__init__.py` - Package initializers

### Documentation:
- `UPPERCASE.md` - Major docs (README, CHANGELOG)
- `lowercase-with-hyphens.md` - Guide docs
- `lowercase-with-hyphens.html` - Web docs

### Configuration:
- `.lowercase` - Hidden config files (.env, .gitignore)
- `lowercase.txt` - Plain text config (requirements.txt)

---

## 🎯 Quick Navigation

**Want to...**
- **Understand the main app?** → `cron_agent.py`
- **Set up the project?** → `setup.py` then `README.md`
- **Add a new platform?** → `scheduler/base.py` (study interface), then create new file
- **Configure settings?** → `.env`
- **Check logs?** → `logs/` (technical) or `clean_logs/` (conversations)
- **Learn how to use?** → `docs/setup-guide.html`
- **Understand architecture?** → `IMPLEMENTATION_SUMMARY.md`
- **See version history?** → `CHANGELOG.md`
- **Understand file structure?** → You're reading it! 😊

---

## 🔄 File Lifecycle

### On First Setup:
1. User runs `python3 setup.py`
2. Creates `venv/` directory
3. Creates `.env` from `.env.example`
4. Installs packages to `venv/lib/`

### On First Run:
1. User runs `./venv/bin/python cron_agent.py --install`
2. Creates scheduler config (plist/service/crontab/task)
3. Starts scheduler

### During Execution:
1. Scheduler triggers `cron_agent.py` every N minutes
2. Creates/appends to `logs/stdout.log`
3. Creates/appends to `logs/stderr.log`
4. Creates/appends to `clean_logs/conversation_YYYY-MM-DD.log`

---

## 📚 Related Documentation

- **Main README**: `README.md` - Getting started guide
- **Setup Guide**: `docs/setup-guide.html` - Interactive HTML guide
- **Implementation**: `IMPLEMENTATION_SUMMARY.md` - Technical details
- **Changes**: `CHANGELOG.md` - Version history
- **This File**: `docs/FILE_STRUCTURE.md` - What you're reading

---

**Last Updated**: February 15, 2025  
**Version**: 2.0.0 - Cross-Platform Edition

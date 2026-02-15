# 📂 Cron Agent - File Structure Documentation

**Last Updated**: February 15, 2026  
**Version**: 2.0.0 (Cross-Platform Edition)

---

## 📋 Table of Contents

- [Overview](#overview)
- [User-Facing Structure](#user-facing-structure)
- [Technical Structure (src/)](#technical-structure-src)
- [Directory Descriptions](#directory-descriptions)
- [File Statistics](#file-statistics)
- [Navigation Guide](#navigation-guide)

---

## 🎯 Overview

The Cron Agent project is organized into **two main areas**:

1. **Root Directory** (User-Facing) - What users interact with
2. **src/ Directory** (Technical) - Implementation code users don't need to touch

This separation makes the project **user-friendly** while keeping technical complexity hidden.

---

## 🌟 User-Facing Structure

```
cron-agent/
├── .env                    # 🔑 Your Todoist API token (EDIT THIS)
├── .env.example            # 📝 Token configuration template
├── config.json             # ⚙️ User settings (polling rate, directories)
│
├── setup                   # 🚀 Setup command (./setup)
├── cronagent              # 🎮 Main command (./cronagent [options])
│
├── logs/                   # 📊 Technical logs (stderr, stdout)
│   ├── stdout.log         # Standard output from agent
│   └── stderr.log         # Error output from agent
│
├── clean_logs/            # 💬 Conversation logs (Cursor AI interactions)
│   └── conversation_*.log # Each task conversation
│
├── docs/                  # 📚 Documentation
│   ├── setup-guide.html  # Interactive setup guide
│   ├── FILE_STRUCTURE.md # This file
│   ├── README.md         # Additional documentation
│   └── (other guides)
│
├── README.md              # 📖 Main project documentation
├── CHANGELOG.md           # 📜 Version history
└── IMPLEMENTATION_SUMMARY.md  # 🏗️ Technical implementation details
```

### 🔑 Key User Files

#### `.env` (Configuration)
```bash
# Your Todoist API token
TODOIST_TOKEN=your_token_here
```
**This is the ONLY file you must edit!**

#### `config.json` (Settings)
```json
{
  "polling_interval_minutes": 5,
  "log_directory": "logs",
  "clean_log_directory": "clean_logs"
}
```
**Adjust polling rate and log directories here**

---

## 🔧 Technical Structure (src/)

```
src/
├── cron_agent.py          # 🤖 Main application entry point
├── setup.py               # 📦 Cross-platform setup script
├── requirements.txt       # 📋 Python dependencies
│
├── scheduler/             # ⏰ OS-specific scheduling implementations
│   ├── __init__.py       # Package initialization
│   ├── factory.py        # Factory pattern for OS detection
│   ├── base.py           # Abstract base scheduler
│   ├── launchd.py        # macOS LaunchAgent implementation
│   ├── systemd.py        # Linux systemd implementation
│   ├── cron.py           # Linux cron fallback
│   └── windows_task.py   # Windows Task Scheduler implementation
│
├── analyze_clean_logs.py  # 📊 Log analysis utility
├── view_clean_logs.sh     # 👁️ Log viewing utility
│
└── venv/                  # 🐍 Python virtual environment (not committed)
    ├── bin/              # Executables (Unix)
    ├── Scripts/          # Executables (Windows)
    └── lib/              # Python packages
```

---

## 📁 Directory Descriptions

### Root Level Files

#### Executable Scripts

| File | Purpose | Usage |
|------|---------|-------|
| `setup` | Setup launcher | `./setup` |
| `cronagent` | Agent launcher | `./cronagent [options]` |

**Examples:**
```bash
# Setup project
./setup

# Install scheduler
./cronagent --install

# Check status
./cronagent --status

# Uninstall
./cronagent --uninstall
```

#### Configuration Files

| File | Purpose | Edit? |
|------|---------|-------|
| `.env` | API token | ✅ Yes (required) |
| `.env.example` | Token template | No (copy to .env) |
| `config.json` | User settings | ✅ Yes (optional) |
| `.gitignore` | Git ignore rules | No |

#### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `CHANGELOG.md` | Version history |
| `IMPLEMENTATION_SUMMARY.md` | Technical details |

### Root Level Directories

#### `logs/` - Technical Logs
- **Purpose**: Technical debugging information
- **Files**:
  - `stdout.log` - Standard output from agent execution
  - `stderr.log` - Error messages and warnings
- **Created by**: OS scheduler (LaunchAgent, systemd, etc.)
- **Rotation**: Managed by OS scheduler

#### `clean_logs/` - Conversation Logs
- **Purpose**: Human-readable Cursor AI conversations
- **Format**: `conversation_YYYYMMDD_HHMMSS.log`
- **Contents**: Task prompts and AI responses
- **Created by**: Cron agent during task execution

#### `docs/` - Documentation
- **Purpose**: All project documentation
- **Key files**:
  - `setup-guide.html` - Interactive setup guide with OS-specific tabs
  - `FILE_STRUCTURE.md` - This document
  - `README.md` - General documentation
  - Other guides and summaries

---

### `src/` Directory Files

#### Core Application Files

##### `cron_agent.py` (Main Application)
**Purpose**: Core agent logic and entry point

**Key Components**:
- `CronAgent` class - Main agent implementation
- Task polling from Todoist
- Cursor AI integration
- Clean log management
- CLI argument parsing (`--install`, `--uninstall`, `--status`)

**CLI Options**:
```bash
python src/cron_agent.py --install   # Install scheduler
python src/cron_agent.py --uninstall # Uninstall scheduler
python src/cron_agent.py --status    # Check status
python src/cron_agent.py --interval 10  # Set interval (minutes)
```

##### `setup.py` (Setup Script)
**Purpose**: Cross-platform setup automation

**Features**:
- Python version verification
- Virtual environment creation
- Dependency installation
- `.env` file setup
- Color-coded terminal output

**Platform Support**: macOS, Linux, Windows

##### `requirements.txt` (Dependencies)
**Python packages**:
```
requests>=2.31.0      # HTTP requests
python-dotenv>=1.0.0  # Environment variables
schedule>=1.2.0       # Task scheduling
```

---

#### `scheduler/` Directory

**Purpose**: OS-specific scheduling implementations using **Factory** and **Strategy** design patterns.

##### `factory.py` (Factory Pattern)
**Purpose**: Detect OS and create appropriate scheduler

**Logic**:
```python
if macOS:
    return LaunchdScheduler
elif Linux:
    if systemd available:
        return SystemdScheduler
    else:
        return CronScheduler
elif Windows:
    return WindowsTaskScheduler
```

##### `base.py` (Abstract Base)
**Purpose**: Common interface for all schedulers

**Abstract Methods**:
- `install()` - Install scheduler
- `uninstall()` - Remove scheduler
- `is_installed()` - Check if installed
- `start()` - Start scheduler
- `stop()` - Stop scheduler
- `status()` - Get status information

##### Platform-Specific Implementations

| File | OS | Scheduler | Configuration |
|------|-----|-----------|---------------|
| `launchd.py` | macOS | LaunchAgent | `.plist` in `~/Library/LaunchAgents/` |
| `systemd.py` | Linux | systemd timer | `.service` + `.timer` in `~/.config/systemd/user/` |
| `cron.py` | Linux | cron | `crontab` entry |
| `windows_task.py` | Windows | Task Scheduler | `schtasks.exe` |

**Example - macOS LaunchAgent plist**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" ...>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cursor.cronagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python3</string>
        <string>/path/to/src/cron_agent.py</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer> <!-- 5 minutes -->
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

---

#### Utility Files

##### `analyze_clean_logs.py` (Log Analysis)
**Purpose**: Analyze conversation logs for statistics

**Features**:
- Count total conversations
- Analyze task types
- Show time distribution
- Success/failure rates

**Usage**:
```bash
python src/analyze_clean_logs.py
```

##### `view_clean_logs.sh` (Log Viewer)
**Purpose**: View conversation logs with formatting

**Usage**:
```bash
./src/view_clean_logs.sh
```

---

### `venv/` Directory (Virtual Environment)

**Purpose**: Isolated Python environment for project dependencies

**Structure**:
```
venv/
├── bin/          # Unix executables (python3, pip3)
├── Scripts/      # Windows executables (python.exe, pip.exe)
├── lib/          # Python packages
│   └── python3.x/
│       └── site-packages/
└── pyvenv.cfg    # Virtual environment config
```

**Not committed to git** (ignored via `.gitignore`)

---

## 📊 File Statistics

### Total Files

| Category | Count |
|----------|-------|
| Root Level Files | 8 |
| Documentation Files | 7+ |
| Python Source Files | 12 |
| Configuration Files | 3 |
| Scripts | 3 |

### Lines of Code (Approx.)

| Component | Lines |
|-----------|-------|
| `cron_agent.py` | ~500 |
| `setup.py` | ~250 |
| Scheduler implementations | ~800 |
| Utilities | ~300 |
| **Total** | **~1850** |

---

## 🗺️ Navigation Guide

### For Users

**Files you interact with:**
```
.env                # Edit: Add your token
config.json         # Edit: Adjust settings
setup               # Run: ./setup
cronagent           # Run: ./cronagent --install
logs/               # Check: Technical logs
clean_logs/         # Check: Conversation logs
docs/               # Read: Documentation
```

**Files you don't need to touch:**
```
src/                # Technical code (hidden complexity)
.gitignore          # Git configuration
IMPLEMENTATION_SUMMARY.md  # Technical details
```

---

### For Developers

**Start here:**
1. `README.md` - Project overview
2. `IMPLEMENTATION_SUMMARY.md` - Architecture
3. `src/cron_agent.py` - Main application
4. `src/scheduler/factory.py` - OS detection
5. `src/scheduler/base.py` - Scheduler interface

**Testing:**
```bash
# Setup
./setup

# Install
./cronagent --install

# Check status
./cronagent --status

# View logs
tail -f logs/stdout.log
cat clean_logs/conversation_*.log
```

---

## 🔗 Dependencies

### Python Packages (from `requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | >=2.31.0 | HTTP requests to Todoist API |
| `python-dotenv` | >=1.0.0 | Load `.env` file |
| `schedule` | >=1.2.0 | Task scheduling |

### System Dependencies

| OS | Requirements |
|----|--------------|
| **macOS** | Python 3.7+, `launchctl` |
| **Linux** | Python 3.7+, `systemd` or `cron` |
| **Windows** | Python 3.7+, `schtasks.exe` |

---

## 📝 File Naming Conventions

### Log Files
- Technical logs: `stdout.log`, `stderr.log`
- Conversation logs: `conversation_YYYYMMDD_HHMMSS.log`

### Configuration Files
- User config: `.env`, `config.json`
- OS-specific: `.plist`, `.service`, `.timer`

### Python Files
- Entry points: `cron_agent.py`, `setup.py`
- Modules: snake_case (e.g., `base.py`, `factory.py`)
- Classes: PascalCase (e.g., `LaunchdScheduler`, `CronAgent`)

---

## 🔄 File Lifecycle

### Setup Phase
1. User runs `./setup`
2. Creates `src/venv/`
3. Installs dependencies
4. Creates `.env` from `.env.example`

### Installation Phase
1. User runs `./cronagent --install`
2. Creates OS-specific scheduler configuration
3. Creates `logs/` and `clean_logs/` directories
4. Starts scheduler

### Execution Phase
1. OS scheduler runs `src/cron_agent.py` every N minutes
2. Agent polls Todoist API
3. Executes tasks via Cursor AI
4. Writes to `logs/stdout.log` and `logs/stderr.log`
5. Saves conversations to `clean_logs/`

### Uninstallation Phase
1. User runs `./cronagent --uninstall`
2. Stops scheduler
3. Removes OS-specific configuration
4. Logs remain for review

---

## 🎯 Key Takeaways

### For Users:
- **Only edit**: `.env` and `config.json`
- **Run**: `./setup` and `./cronagent`
- **Check**: `logs/` and `clean_logs/`
- **Ignore**: Everything in `src/`

### For Developers:
- **Architecture**: Factory + Strategy pattern
- **Entry point**: `src/cron_agent.py`
- **OS handling**: `src/scheduler/`
- **Testing**: Use `--install`, `--status`, `--uninstall`

---

## 📚 Related Documentation

- [README.md](../README.md) - Main project documentation
- [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) - Technical architecture
- [CHANGELOG.md](../CHANGELOG.md) - Version history
- [setup-guide.html](./setup-guide.html) - Interactive setup guide

---

**Project**: Cron Agent  
**Version**: 2.0.0  
**Last Updated**: February 15, 2026  
**Author**: [Your Name]

---

_For questions or issues, check the documentation or create a GitHub issue._

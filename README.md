# 🤖 Cron Agent - Cross-Platform Task Automation

**Intelligent task automation system** that reads tasks from Todoist, executes them via Cursor AI, and updates results automatically.

## ✨ Features

- 🌍 **Cross-Platform**: Works on macOS, Linux, and Windows
- ⏰ **Smart Scheduling**: Uses native schedulers (LaunchAgents/systemd/cron/Task Scheduler)
- 🤖 **AI Integration**: Processes tasks with Cursor AI
- 📝 **Clean Logs**: Separate technical and conversation logs
- 📊 **Statistics**: Real-time execution statistics
- 🔄 **Auto-sync**: Automatic Todoist integration

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (only requirement!)
- Todoist account with API token

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd cron-agent

# Run cross-platform setup
python3 setup.py        # macOS/Linux
python setup.py         # Windows
```

### Configuration

1. **Get Todoist API Token**:
   - Visit: https://todoist.com/app/settings/integrations/developer
   - Copy your API Token

2. **Configure `.env` file**:
   ```bash
   # Edit .env file
   nano .env
   
   # Add your token
   TODOIST_TOKEN=your_token_here
   ```

3. **Install Scheduler**:
   ```bash
   python3 cron_agent.py --install
   ```

### Usage

```bash
# Check status
python3 cron_agent.py --status

# Manual run (for testing)
python3 cron_agent.py

# Uninstall scheduler
python3 cron_agent.py --uninstall
```

---

## 🏗️ Architecture

### Cross-Platform Design

The system uses an **abstraction layer** that automatically detects your OS and uses the appropriate scheduler:

```
┌─────────────────────────────────────┐
│        cron_agent.py                │
│     (Core Logic - OS Agnostic)      │
└───────────┬─────────────────────────┘
            │
    ┌───────┴────────┐
    │ scheduler/     │
    │  factory.py    │
    │ (Auto-detect)  │
    └───────┬────────┘
            │
    ┌───────┴────────────────┐
    │                        │
┌───▼────┐  ┌────▼─────┐  ┌─▼────────┐
│ macOS  │  │  Linux   │  │ Windows  │
│LaunchD │  │systemd   │  │   Task   │
│        │  │  /cron   │  │Scheduler │
└────────┘  └──────────┘  └──────────┘
```

### Directory Structure

```
cron-agent/
├── cron_agent.py           # Main application
├── setup.py               # Cross-platform setup script
├── requirements.txt       # Python dependencies
├── .env                   # Configuration (not committed)
│
├── scheduler/             # Scheduler abstraction layer
│   ├── __init__.py
│   ├── base.py           # Abstract base class
│   ├── factory.py        # OS detection & factory
│   ├── launchd.py        # macOS LaunchAgents
│   ├── systemd.py        # Linux systemd timers
│   ├── cron.py           # Linux cron (fallback)
│   └── windows_task.py   # Windows Task Scheduler
│
├── logs/                  # Technical logs (stdout/stderr)
├── clean_logs/           # Conversation logs (prompts/responses)
├── docs/                 # Documentation
│   └── setup-guide.html  # Interactive setup guide
│
└── venv/                 # Virtual environment (auto-created)
```

---

## 📖 Platform-Specific Details

### macOS (LaunchAgents)

**Features**:
- ✅ Survives sleep/wake cycles
- ✅ No sudo required
- ✅ Runs on user login
- ✅ Native macOS integration

**Location**: `~/Library/LaunchAgents/com.cursor.cronagent.plist`

**Management**:
```bash
# Install
python3 cron_agent.py --install

# Check status
launchctl list | grep cronagent

# View logs
tail -f logs/stdout.log

# Uninstall
python3 cron_agent.py --uninstall
```

---

### Linux (systemd or cron)

**systemd** (preferred, modern distros):
- ✅ Reliable scheduling
- ✅ Built-in logging (journalctl)
- ✅ No sudo required (user units)

**Location**: `~/.config/systemd/user/cronagent.{service,timer}`

**Management**:
```bash
# Install
python3 cron_agent.py --install

# Check status
systemctl --user status cronagent.timer

# View logs
journalctl --user -u cronagent.service -f

# Uninstall
python3 cron_agent.py --uninstall
```

**cron** (fallback, universal):
- ✅ Works on all Linux systems
- ✅ Simple and reliable
- ⚠️ May miss schedules if system sleeping

**Location**: User crontab

**Management**:
```bash
# Install
python3 cron_agent.py --install

# Check crontab
crontab -l

# View logs
tail -f logs/cron.log

# Uninstall
python3 cron_agent.py --uninstall
```

---

### Windows (Task Scheduler)

**Features**:
- ✅ Native Windows integration
- ✅ GUI management available
- ✅ Survives sleep/hibernate
- ⚠️ May require admin privileges

**Location**: Task Scheduler Library

**Management**:
```bash
# Install
python cron_agent.py --install

# Check status (CLI)
schtasks /Query /TN "CursorCronAgent" /FO LIST

# Check status (GUI)
# Press Win+R, type: taskschd.msc

# Uninstall
python cron_agent.py --uninstall
```

---

## 📝 Logging

### Two Types of Logs

1. **Technical Logs** (`logs/`):
   - stdout.log - Standard output
   - stderr.log - Error messages
   - Full debugging information

2. **Clean Logs** (`clean_logs/`):
   - conversation_YYYY-MM-DD.log
   - Only prompts and AI responses
   - Perfect for presentations/documentation

### View Logs

```bash
# View clean logs (conversations only)
./view_clean_logs.sh

# Analyze logs (statistics)
python analyze_clean_logs.py

# View technical logs
tail -f logs/stdout.log
```

---

## 🔧 Configuration

### Scheduler Interval

Default: 5 minutes

Change during installation:
```bash
python3 cron_agent.py --install --interval 10  # 10 minutes
```

### Environment Variables

Edit `.env` file:
```bash
# Todoist Configuration
TODOIST_TOKEN=your_token_here

# Optional: Custom log directory
CLEAN_LOGS_DIR=clean_logs
```

---

## 🛠️ Development

### Setup Development Environment

```bash
# Install with dev dependencies
python3 setup.py

# Run tests
pytest tests/

# Format code
black cron_agent.py scheduler/

# Lint
flake8 cron_agent.py scheduler/
```

### Manual Testing

```bash
# Run once manually (without scheduler)
./venv/bin/python cron_agent.py

# Test with specific token
TODOIST_TOKEN=test_token ./venv/bin/python cron_agent.py
```

---

## 🚨 Troubleshooting

### "Module not found" error

**Problem**: Running with system Python instead of venv

**Solution**:
```bash
# Use venv Python
./venv/bin/python cron_agent.py --status  # macOS/Linux
.\venv\Scripts\python cron_agent.py --status  # Windows
```

### Scheduler not running

**macOS**:
```bash
# Check if loaded
launchctl list | grep cronagent

# Reload
python3 cron_agent.py --uninstall
python3 cron_agent.py --install
```

**Linux (systemd)**:
```bash
# Check timer status
systemctl --user status cronagent.timer

# Check last run
systemctl --user list-timers

# Reload
systemctl --user daemon-reload
systemctl --user restart cronagent.timer
```

**Linux (cron)**:
```bash
# Check crontab
crontab -l

# Check syslog
grep CRON /var/log/syslog
```

**Windows**:
```bash
# Check task
schtasks /Query /TN "CursorCronAgent" /V /FO LIST

# Run manually
schtasks /Run /TN "CursorCronAgent"
```

### No tasks being processed

1. **Check Todoist token**:
   ```bash
   cat .env
   # Verify TODOIST_TOKEN is set
   ```

2. **Test API connection**:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        https://api.todoist.com/rest/v2/tasks
   ```

3. **Check logs**:
   ```bash
   tail -f logs/stdout.log
   tail -f logs/stderr.log
   ```

---

## 📊 Statistics

View real-time statistics:
```bash
# Analyze conversation logs
python analyze_clean_logs.py

# View in clean log files
tail -n 20 clean_logs/conversation_$(date +%Y-%m-%d).log
```

---

## 🔐 Security

- ✅ API tokens stored in `.env` (not committed to git)
- ✅ Runs in user context (no root/admin required on macOS/Linux)
- ✅ Logs stored locally
- ⚠️ Keep `.env` file secure

---

## 📚 Documentation

- **Interactive Setup Guide**: Open `docs/setup-guide.html` in browser
- **Changelog**: See `CHANGELOG.md`
- **Clean Logs Guide**: See `CLEAN_LOGS_GUIDE.md`

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📄 License

[Add your license here]

---

## 🙏 Acknowledgments

- Todoist API for task management
- Cursor AI for intelligent execution
- Python community for excellent libraries

---

## 📞 Support

- Issues: [GitHub Issues](your-repo-url/issues)
- Documentation: [Wiki](your-repo-url/wiki)
- Email: your-email@example.com

---

**Built with ❤️ for cross-platform automation**

Version: 2.0.0 - Cross-Platform Edition

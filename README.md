# 🤖 Cron Agent - Cross-Platform Task Automation

**Intelligent task automation** that reads tasks from Todoist, executes them via Cursor AI, and updates results automatically.

✅ Works on **macOS, Linux, and Windows**  
⏰ Smart scheduling with native OS schedulers  
📝 Clean conversation logs  
🔒 Secure local configuration

---

## 🚀 Quick Start (3 Steps)

### 1. Setup
```bash
./setup
```
This installs everything you need (takes ~30 seconds).

### 2. Configure Your Token
Edit the `.env` file and add your Todoist API token:
```bash
nano .env
```
```bash
TODOIST_TOKEN=your_token_here
```

Get your token from: https://todoist.com/app/settings/integrations/developer

### 3. Install Scheduler
```bash
./cronagent --install
```

**That's it! 🎉** Your agent is now running automatically every 5 minutes.

---

## 📋 What You Need to Know

### User Files (What You'll Work With):

```
cron-agent/
├── .env                   # 🔑 Your Todoist token (EDIT THIS)
├── config.json            # ⚙️ Settings (polling rate, directories)
│
├── logs/                  # 📊 Technical logs (debugging)
├── clean_logs/            # 💬 Conversation logs (prompts & responses)
│
├── docs/                  # 📚 Documentation
│   ├── setup-guide.html  # Interactive setup guide
│   └── FILE_STRUCTURE.md # Project structure reference
│
└── src/                   # 🔧 Code (you don't need to touch this)
```

### The Important Files:

#### `.env` (Your Token)
```bash
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
**Adjust polling rate if needed** (default: 5 minutes)

---

## 🎮 Usage

### Basic Commands:

```bash
# Install scheduler (first time)
./cronagent --install

# Check if it's running
./cronagent --status

# Stop scheduler
./cronagent --uninstall

# Manual run (for testing)
./cronagent
```

### Viewing Logs:

```bash
# View conversation logs (clean)
cat clean_logs/conversation_*.log

# View technical logs
tail -f logs/stdout.log
```

---

## 🔧 Configuration

### Change Polling Interval

Edit `config.json`:
```json
{
  "polling_interval_minutes": 10
}
```

Then reinstall:
```bash
./cronagent --uninstall
./cronagent --install
```

---

## 📚 Documentation

- **Interactive Setup Guide**: Open `docs/setup-guide.html` in your browser
  - Tabs for macOS, Linux, Windows
  - Step-by-step instructions
  - Comparison tables

- **File Structure Guide**: `docs/FILE_STRUCTURE.md`
  - Complete project organization
  - What each file does
  - Where everything is located

- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
  - Technical architecture
  - Design decisions
  - Platform comparisons

- **Version History**: `CHANGELOG.md`
  - What changed in each version

---

## 🌍 Platform Support

| Platform | Scheduler | Status |
|----------|-----------|--------|
| 🍎 **macOS** | LaunchAgents | ✅ Tested |
| 🐧 **Linux** | systemd/cron | ✅ Ready |
| 🪟 **Windows** | Task Scheduler | ✅ Ready |

---

## 🛠️ Troubleshooting

### Scheduler Not Running?

```bash
# Check status
./cronagent --status

# Reinstall
./cronagent --uninstall
./cronagent --install
```

### Can't Find Token?

Make sure `.env` file exists in the root directory:
```bash
ls -la .env
cat .env
```

### No Tasks Being Processed?

1. Check Todoist API connection:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        https://api.todoist.com/rest/v2/tasks
   ```

2. Check logs:
   ```bash
   tail -f logs/stdout.log
   ```

---

## 📂 Project Structure

```
Root Directory (User-Facing):
├── 📝 .env                    # Your token (EDIT THIS)
├── ⚙️ config.json             # Settings
├── 📚 docs/                   # Documentation
├── 📊 logs/                   # Technical logs
├── 💬 clean_logs/             # Conversation logs
├── 🚀 setup                   # Setup command
└── 🎮 cronagent              # Main command

src/ (Technical - No Need to Touch):
├── cron_agent.py             # Main application
├── setup.py                  # Setup script
├── requirements.txt          # Dependencies
├── scheduler/                # Platform-specific code
└── venv/                     # Virtual environment
```

**You only need to work with files in the root directory!**

---

## 🔐 Security

- ✅ Token stored locally in `.env` (not committed to git)
- ✅ Runs in your user context (no root/admin needed on macOS/Linux)
- ✅ All data stays on your machine
- ✅ No cloud services required

---

## 🤝 Contributing

See `docs/CONTRIBUTING.md` (if you want to modify the code)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/natovichat/cron-agent/issues)
- **Documentation**: Check `docs/` directory
- **Email**: [Your email]

---

## 📄 License

[Add your license]

---

## 🎯 Key Features

- 🌍 **Cross-Platform**: Works everywhere (macOS, Linux, Windows)
- ⏰ **Native Scheduling**: Uses best scheduler per OS
- 🤖 **AI Integration**: Cursor AI task processing
- 📝 **Clean Logs**: Separate technical and conversation logs
- 🔒 **Secure**: Local-only, no cloud dependencies
- 🎨 **User-Friendly**: Simple commands, clear structure
- 📊 **Statistics**: Real-time execution stats

---

## 🏆 Version

**v2.0.0** - Cross-Platform Edition

See `CHANGELOG.md` for version history.

---

**Built with ❤️ for cross-platform automation**

Need help? Check `docs/setup-guide.html` for detailed instructions!

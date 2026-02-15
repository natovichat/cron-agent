# OS-Level Scheduling Architecture

## Overview

The Cron Agent uses **native OS schedulers** instead of a continuously running Python process. This is more efficient, reliable, and follows OS best practices.

## Architecture Principle

```
❌ OLD WAY: Long-running Python process
Python → while True → schedule library → check every N seconds

✅ NEW WAY: OS-level scheduling
OS Scheduler → Runs Python script → Process tasks → Exit
    ↓                                        ↓
  (every N minutes)                    (clean exit)
```

### Key Benefits

1. **Resource Efficient**: Python process only runs when needed
2. **Reliable**: OS schedulers survive sleep/wake, restarts
3. **Battle-tested**: Uses proven OS scheduling infrastructure
4. **No zombies**: No long-running processes that might hang
5. **Better logging**: Each run is isolated in logs

---

## How It Works by Platform

### macOS: LaunchAgent

**Scheduler**: `launchd` (Apple's init system)

**Configuration File**: `~/Library/LaunchAgents/com.cursor.cronagent.plist`

```xml
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cursor.cronagent</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python3</string>
        <string>/path/to/src/cron_agent.py</string>
        <string>--once</string>  <!-- ✨ Single run mode -->
    </array>
    
    <key>StartInterval</key>
    <integer>300</integer>  <!-- Run every 5 minutes -->
    
    <key>RunAtLoad</key>
    <true/>  <!-- Run immediately after load -->
    
    <key>WorkingDirectory</key>
    <string>/path/to/project</string>
</dict>
</plist>
```

**How it executes**:
```
launchd (always running)
  ↓
  Every 5 minutes: python3 cron_agent.py --once
  ↓
  Script processes tasks and exits
  ↓
  launchd waits 5 minutes
  ↓
  Repeats...
```

**Benefits**:
- ✅ Runs on login (no manual start needed)
- ✅ Survives sleep/wake cycles
- ✅ No sudo required (user-level)
- ✅ Integrated with macOS

---

### Linux: systemd Timer

**Scheduler**: `systemd` (modern Linux init system)

**Configuration Files**:
- **Service**: `~/.config/systemd/user/cursor-cronagent.service`
- **Timer**: `~/.config/systemd/user/cursor-cronagent.timer`

**Service File**:
```ini
[Unit]
Description=Cursor Cron Agent
After=network.target

[Service]
Type=oneshot
ExecStart=/path/to/venv/bin/python3 /path/to/src/cron_agent.py --once
WorkingDirectory=/path/to/project
```

**Timer File**:
```ini
[Unit]
Description=Cursor Cron Agent Timer

[Timer]
OnBootSec=1min           # Run 1 minute after boot
OnUnitActiveSec=5min     # Then every 5 minutes
Persistent=true          # Catch up if system was off

[Install]
WantedBy=timers.target
```

**How it executes**:
```
systemd (always running)
  ↓
  Timer triggers service
  ↓
  Service runs: python3 cron_agent.py --once
  ↓
  Script exits (Type=oneshot)
  ↓
  Timer waits 5 minutes
  ↓
  Repeats...
```

**Benefits**:
- ✅ Modern Linux standard
- ✅ Persistent (catches up if offline)
- ✅ User-level (no sudo)
- ✅ Integrated logging via journald

---

### Linux: Cron (Fallback)

**Scheduler**: `cron` (traditional Unix scheduler)

**Configuration**: User crontab (`crontab -e`)

```bash
# Cursor Cron Agent
*/5 * * * * cd /path/to/project && /path/to/venv/bin/python3 /path/to/src/cron_agent.py --once >> logs/cron.log 2>&1
```

**Cron Expression**: `*/5 * * * *` = Every 5 minutes

**How it executes**:
```
crond (always running)
  ↓
  Every 5 minutes: python3 cron_agent.py --once
  ↓
  Script exits
  ↓
  Repeats...
```

**Benefits**:
- ✅ Universal Linux compatibility
- ✅ Simple and reliable
- ✅ No systemd required

---

### Windows: Task Scheduler

**Scheduler**: Windows Task Scheduler

**Configuration**: Task Scheduler entry

```xml
Task Name: CursorCronAgent
Trigger: Every 5 minutes
Action: Run program
  Program: C:\path\to\venv\Scripts\python.exe
  Arguments: C:\path\to\src\cron_agent.py --once
  Start in: C:\path\to\project
```

**How it executes**:
```
Task Scheduler Service (always running)
  ↓
  Every 5 minutes: python.exe cron_agent.py --once
  ↓
  Script exits
  ↓
  Repeats...
```

**Benefits**:
- ✅ Native Windows scheduling
- ✅ GUI management available
- ✅ Reliable execution

---

## Script Execution Modes

The `cron_agent.py` script has two execution modes:

### 1. Single Run Mode (`--once`)

**Used by**: OS schedulers (LaunchAgent/systemd/cron/Task Scheduler)

**Behavior**:
```python
python3 cron_agent.py --once

# → Loads .env
# → Connects to Todoist
# → Processes all tasks
# → Updates Todoist
# → Prints stats
# → Exits (return to OS scheduler)
```

**Output**:
```
🚀 Cron Agent - Single Run
📝 Clean log: clean_logs/conversation_2026-02-15.log
==================================================
⏰ 2026-02-15 14:30:00
==================================================
📋 Found 2 active tasks

📝 Processing task: Calculate 10 + 5
🤖 Cursor AI processing: Calculate 10 + 5
   Using Cursor CLI...
   ✅ Got response from Cursor AI
✅ Task completed successfully

📝 Processing task: Send report
🤖 Cursor AI processing: Send report
   ✅ Got response from Cursor AI
✅ Task completed successfully

--------------------------------------------------
📊 Statistics:
   🎯 Total tasks: 2
   ✅ Successful: 2
   ❌ Failed: 0
   ⏱️  Uptime: 0:00:45
--------------------------------------------------

✅ Run complete
```

**Key Points**:
- ✨ Runs once and exits
- ⏱️ Typically completes in 10-60 seconds
- 🔄 OS scheduler handles next execution
- 📝 Each run appends to logs

---

### 2. Continuous Mode (Manual Testing)

**Used by**: Manual runs without `--once` flag

**Behavior**:
```python
python3 cron_agent.py

# → Loads .env
# → Enters while True loop
# → Uses Python schedule library
# → Runs every N seconds
# → Never exits (until Ctrl+C)
```

**Output**:
```
🚀 Cron Agent - Continuous Mode (Testing)
⏰ Will run every 300 seconds
📝 Clean log: clean_logs/conversation_2026-02-15.log
🛑 Press Ctrl+C to stop

ℹ️  Note: This mode is for testing only.
   For production, use OS scheduler: ./cronagent install
==================================================
[Runs continuously until stopped]
```

**Use Cases**:
- 🧪 Testing before installation
- 🐛 Debugging issues
- 📝 Development
- ⚙️ Custom scenarios

**NOT RECOMMENDED for production!**

---

## Installation Flow

When you run `./cronagent install`:

### Step 1: Detect Platform

```python
# src/scheduler/factory.py
def create_scheduler(script_path, interval_minutes):
    os_name = platform.system()
    
    if os_name == "Darwin":  # macOS
        return LaunchdScheduler(script_path, interval_minutes)
    
    elif os_name == "Linux":
        # Try systemd first
        if has_systemd():
            return SystemdScheduler(script_path, interval_minutes)
        else:
            return CronScheduler(script_path, interval_minutes)
    
    elif os_name == "Windows":
        return WindowsTaskScheduler(script_path, interval_minutes)
```

### Step 2: Create Configuration

Each scheduler creates its OS-specific configuration:
- **macOS**: Writes plist file
- **Linux (systemd)**: Writes .service and .timer files
- **Linux (cron)**: Updates crontab
- **Windows**: Creates Task Scheduler entry

### Step 3: Register with OS

- **macOS**: `launchctl load`
- **Linux (systemd)**: `systemctl --user enable --now`
- **Linux (cron)**: `crontab` (auto-registered)
- **Windows**: `schtasks /Create`

### Step 4: Verify

```bash
./cronagent status

# Shows:
# - Type: LaunchdScheduler (or SystemdScheduler, etc.)
# - Installed: ✅ Yes
# - Running: ✅ Yes
# - Config: /path/to/config/file
```

---

## Why `--once` Flag?

The `--once` flag tells the script to:

1. **Process tasks once** and exit (no loop)
2. **Let OS handle scheduling** (not Python schedule library)
3. **Clean process lifecycle** (start → work → exit)

### Without `--once` (Old Behavior)

```
OS Scheduler runs script every 5 minutes
  ↓
  Script starts
  ↓
  while True loop (redundant!)
  ↓
  Runs every N seconds internally
  ↓
  Never exits
  ↓
  OS scheduler tries to run again
  ↓
  Multiple instances running!  ❌
```

### With `--once` (Correct Behavior)

```
OS Scheduler runs script every 5 minutes
  ↓
  Script starts
  ↓
  Process tasks once
  ↓
  Exit cleanly
  ↓
  OS scheduler waits
  ↓
  Runs again at next interval
  ↓
  Single instance at a time  ✅
```

---

## Execution Timeline Example

**Scenario**: 5-minute interval, 3 tasks to process

```
14:00:00 - LaunchAgent triggers
14:00:01 - Python starts (--once mode)
14:00:02 - Loads .env, connects to Todoist
14:00:03 - Found 3 tasks
14:00:05 - Task 1: Sent to Cursor CLI
14:00:25 - Task 1: Response received (20s)
14:00:27 - Task 1: Updated in Todoist
14:00:28 - Task 2: Sent to Cursor CLI
14:00:43 - Task 2: Response received (15s)
14:00:44 - Task 2: Updated in Todoist
14:00:45 - Task 3: Sent to Cursor CLI
14:01:05 - Task 3: Response received (20s)
14:01:06 - Task 3: Updated in Todoist
14:01:07 - Printed stats
14:01:08 - Python exits
14:01:08 - LaunchAgent waits 5 minutes
14:05:00 - LaunchAgent triggers again
[Repeat]
```

**Total execution time**: ~68 seconds  
**OS scheduler handles**: Rest of the 5 minutes

---

## Resource Usage Comparison

| Aspect | Continuous Mode | OS Scheduler Mode |
|--------|----------------|-------------------|
| **CPU Usage (idle)** | Constant (Python running) | Zero (not running) |
| **Memory (idle)** | ~50 MB | Zero |
| **Active time** | 100% (always running) | ~1-2% (only when processing) |
| **Reliability** | Can hang/crash | OS restarts automatically |
| **Resource efficiency** | ❌ Poor | ✅ Excellent |

### Example: 24 Hour Period

**Continuous Mode (while True loop)**:
- Python runs: 24 hours straight
- Memory used: 50 MB × 24h = 1.2 GB·hours
- CPU cycles: Constant polling

**OS Scheduler Mode (--once)**:
- Python runs: 288 times × ~30s = 144 minutes (2.4 hours)
- Memory used: 50 MB × 2.4h = 120 MB·hours
- CPU cycles: Only when processing

**Savings**: ~90% less resource usage! 🎉

---

## Monitoring OS Scheduler

### macOS (LaunchAgent)

```bash
# Check if running
launchctl list | grep cursor

# View status
launchctl list com.cursor.cronagent

# View logs
tail -f logs/stdout.log
tail -f logs/stderr.log

# Manual trigger (for testing)
launchctl start com.cursor.cronagent
```

### Linux (systemd)

```bash
# Check status
systemctl --user status cursor-cronagent.timer
systemctl --user status cursor-cronagent.service

# View logs
journalctl --user -u cursor-cronagent.service -f

# Manual trigger
systemctl --user start cursor-cronagent.service

# Check when next run is scheduled
systemctl --user list-timers cursor-cronagent.timer
```

### Linux (cron)

```bash
# View crontab
crontab -l | grep "Cursor Cron Agent"

# View logs
tail -f logs/cron.log

# Manual trigger (edit crontab temporarily)
crontab -e
# Change to: * * * * * (every minute for testing)
```

### Windows (Task Scheduler)

```powershell
# View task status
schtasks /Query /TN CursorCronAgent

# View task details
schtasks /Query /TN CursorCronAgent /V /FO LIST

# Manual trigger
schtasks /Run /TN CursorCronAgent

# View in GUI
taskschd.msc
```

---

## Execution Modes

### Mode 1: OS Scheduler (Production) ✅ Recommended

```bash
# Install
./cronagent install

# The OS scheduler will:
# - Run script every N minutes
# - Pass --once flag automatically
# - Capture logs
# - Restart on boot
```

**Process lifecycle**:
```
Start → Load .env → Connect → Process → Update → Log → Exit
[30-120 seconds total]
```

### Mode 2: Manual Continuous (Testing Only)

```bash
# Run manually
python3 src/cron_agent.py
# or
./cronagent

# Script will:
# - Enter while True loop
# - Use Python schedule library
# - Run continuously until Ctrl+C
```

**Process lifecycle**:
```
Start → while True → schedule.run_pending() → [never exits]
```

---

## Why This Design?

### Traditional Cron Pattern

Following Unix philosophy: "Do one thing and do it well"

1. **Cron/scheduler**: Handles timing
2. **Script**: Handles work
3. **Separation of concerns**: Each does what it's best at

### Process Model

```
❌ Long-running daemon:
- Must handle signals (SIGTERM, SIGHUP)
- Must manage its own lifecycle
- Must handle crashes/hangs
- Requires process monitoring (systemd, supervisord)
- Complex state management

✅ Run-and-exit pattern:
- Simple: do work and exit
- OS handles restart if crash
- No state between runs
- Each run is isolated
- Easier to debug
```

---

## Configuration

### Interval Configuration

Set in `.env`:
```bash
REFRESH_INTERVAL_SECONDS=300  # 5 minutes
```

**When you change it**:
```bash
# Update .env
nano .env
# Change: REFRESH_INTERVAL_SECONDS=600  # 10 minutes

# Reinstall to apply changes
./cronagent uninstall
./cronagent install
```

The scheduler will now run every 10 minutes!

### CLI vs Fallback

```bash
# Enable Cursor CLI (AI mode)
USE_CURSOR_CLI=true

# Disable (simulation mode)
USE_CURSOR_CLI=false
```

---

## Troubleshooting

### Issue: Script Not Running

**Check scheduler status**:
```bash
# macOS
launchctl list com.cursor.cronagent

# Linux (systemd)
systemctl --user status cursor-cronagent.timer

# Linux (cron)
crontab -l | grep cursor

# Windows
schtasks /Query /TN CursorCronAgent
```

### Issue: Multiple Instances Running

**Symptom**: Multiple Python processes running

**Cause**: Probably running in continuous mode (`while True` loop)

**Solution**:
1. Kill manual processes: `pkill -f cron_agent.py`
2. Use OS scheduler: `./cronagent install`
3. Verify: `./cronagent status`

### Issue: Tasks Not Processing

**Check logs**:
```bash
# OS scheduler logs
tail -f logs/stdout.log
tail -f logs/stderr.log

# Conversation logs
cat clean_logs/conversation_*.log
```

**Common issues**:
- Token invalid/expired
- Network connectivity
- Cursor CLI not authenticated
- Python path wrong in scheduler config

---

## Performance Characteristics

### Single Run (--once mode)

**Typical execution time by number of tasks**:

| Tasks | Fallback Mode | CLI Mode (AI) |
|-------|---------------|---------------|
| 0 tasks | ~1s | ~1s |
| 1 task | ~2s | 15-45s |
| 3 tasks | ~5s | 45-120s |
| 5 tasks | ~8s | 75-180s |

**CLI mode is slower but provides real AI responses!**

### Resource Usage per Run

- **Memory**: ~50-100 MB (during execution)
- **CPU**: 5-20% (during execution)
- **Network**: ~10-50 KB per task (API calls)
- **Disk**: ~10 KB per task (logs)

### Daily Resource Usage

**Assumptions**: 5-minute interval, 2 tasks per run

- **Executions per day**: 288 runs (24h × 60min / 5min)
- **Total active time**: ~288 × 30s = 2.4 hours
- **Total idle time**: 21.6 hours (zero resource usage!)

---

## Comparison Table

| Feature | Continuous Mode | OS Scheduler Mode |
|---------|-----------------|-------------------|
| **How it runs** | `while True` loop | OS triggers script |
| **Process lifetime** | Forever (until killed) | 30-120 seconds |
| **Resource usage (idle)** | High (always running) | Zero (not running) |
| **Reliability** | Can hang/crash | Auto-restart by OS |
| **Best for** | Testing/development | Production |
| **Start method** | `python3 cron_agent.py` | `./cronagent install` |
| **Stop method** | Ctrl+C | `./cronagent uninstall` |
| **Survives reboot** | ❌ No | ✅ Yes |
| **Multiple instances** | ⚠️ Possible | 🛡️ Prevented by OS |

---

## Best Practices

### ✅ Do This

1. **Use OS scheduler for production**:
   ```bash
   ./cronagent install
   ```

2. **Use continuous mode for testing only**:
   ```bash
   python3 src/cron_agent.py
   # Test, then Ctrl+C
   ```

3. **Check status regularly**:
   ```bash
   ./cronagent status
   ```

4. **Monitor logs**:
   ```bash
   tail -f logs/stdout.log
   ```

### ❌ Don't Do This

1. **Don't run continuous mode in production**
   - Wastes resources
   - Can cause multiple instances
   - Doesn't survive reboots

2. **Don't skip the `--once` flag in schedulers**
   - Script will loop forever
   - Multiple instances will spawn
   - Resource exhaustion

3. **Don't modify scheduler configs manually**
   - Use `./cronagent` commands
   - Let the code manage configs

---

## Technical Details

### Process Flow Diagram

```
┌─────────────────────────────────────────────────┐
│ OS Scheduler (launchd/systemd/cron)            │
│ - Runs continuously                             │
│ - Handles timing                                │
│ - Monitors script exit codes                    │
└──────────────────┬──────────────────────────────┘
                   │
                   │ Every N minutes
                   ▼
┌──────────────────────────────────────────────────┐
│ Python Script (cron_agent.py --once)            │
│                                                  │
│ 1. Load environment (.env)                      │
│ 2. Connect to Todoist API                       │
│ 3. Fetch active tasks                           │
│ 4. For each task:                               │
│    ├─ Send to Cursor CLI                        │
│    ├─ Wait for AI response                      │
│    ├─ Add comment to task                       │
│    └─ Mark task complete                        │
│ 5. Print statistics                             │
│ 6. Exit with code 0                             │
│                                                  │
│ Duration: 10-120 seconds                        │
└──────────────────┬──────────────────────────────┘
                   │
                   │ Exit code 0
                   ▼
┌──────────────────────────────────────────────────┐
│ OS Scheduler                                     │
│ - Sees script exited cleanly                    │
│ - Waits for next interval                       │
│ - Repeats cycle                                 │
└──────────────────────────────────────────────────┘
```

### Error Handling

If script exits with non-zero code:
- **macOS/Linux**: Logged, waits for next interval
- **Windows**: Logged, scheduler continues
- **All**: OS scheduler handles retry automatically

---

## Summary

| Aspect | Value |
|--------|-------|
| **Scheduling** | OS-level (launchd/systemd/cron) |
| **Script Mode** | `--once` (single run) |
| **Process Model** | Run → Process → Exit |
| **Resource Usage** | Minimal (~90% savings) |
| **Reliability** | High (OS-managed) |
| **Production Ready** | ✅ Yes |

**The agent uses industry-standard OS scheduling, not a custom daemon!**

---

**Last Updated**: 2026-02-15

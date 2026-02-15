# Cursor CLI is Now Mandatory

## Summary

**Breaking Change**: Cursor CLI is now **required** for the Cron Agent to function. There is no fallback mode.

---

## What Changed

### 1. Setup Validation (REQUIRED)

During `./cronagent setup`, the agent now:

✅ **Verifies Cursor CLI is installed**
- Checks for `cursor` command in PATH
- Exits with error if not found
- Provides installation instructions

✅ **Forces Cursor CLI login**
- Prompts user to login
- No skip option
- Exits if login fails

❌ **Setup fails if:**
- Cursor CLI not installed
- User skips login
- Login fails or times out

### Error Message Example:

```
❌ ERROR: Cursor CLI is required but not found

Cursor CLI is mandatory for this agent to work.

Installation Instructions:
1. Visit: https://cursor.sh
2. Download and install Cursor
3. Open Cursor and go to Settings
4. Enable CLI by running in Cursor terminal:
   Cursor > Install 'cursor' command
5. Or run manually: ln -s /Applications/Cursor.app/Contents/Resources/app/bin/cursor /usr/local/bin/cursor

After installing Cursor CLI, run setup again:
   ./cronagent setup
```

---

### 2. Removed Fallback Mode

**What was removed:**

❌ `USE_CURSOR_CLI` environment variable
❌ `use_cli` parameter from CursorAgent
❌ `_analyze_and_execute()` method (simulation)
❌ `_perform_calculation()` method (local calculations)
❌ All fallback logic

**Why removed:**
- Fallback mode provided inferior experience
- Inconsistent behavior confused users
- Mandatory CLI ensures quality
- Simpler codebase, easier to maintain

---

### 3. CursorAgent Validation

The `CursorAgent` class now:

```python
def __init__(self, clean_logger=None, code_location=None):
    """Initialize Cursor Agent - REQUIRES Cursor CLI"""
    self.cursor_cli_path = self._find_cursor_cli()
    
    # Validate Cursor CLI is available
    if not self.cursor_cli_path:
        print("❌ FATAL ERROR: Cursor CLI is required but not found!")
        print("Installation Instructions...")
        sys.exit(1)
```

**Agent exits immediately if Cursor CLI not found!**

---

### 4. Error Handling Changes

**Before** (fallback mode):
```
Cursor CLI timeout → Falls back to simulation
Cursor CLI error → Falls back to simulation  
Empty response → Falls back to simulation
```

**After** (no fallback):
```
Cursor CLI timeout → Returns error message
Cursor CLI error → Returns error message
Empty response → Returns error message
```

**User must fix Cursor CLI issues to continue.**

---

## Migration Guide

### For New Users

1. **Install Cursor**:
   ```bash
   # Download from: https://cursor.sh
   # Install Cursor application
   ```

2. **Enable Cursor CLI**:
   ```bash
   # In Cursor:
   # Cursor > Install 'cursor' command
   
   # Or manually:
   ln -s /Applications/Cursor.app/Contents/Resources/app/bin/cursor /usr/local/bin/cursor
   ```

3. **Verify Installation**:
   ```bash
   which cursor
   # Should output: /usr/local/bin/cursor (or similar)
   
   cursor --version
   # Should show Cursor version
   ```

4. **Run Setup**:
   ```bash
   ./cronagent setup
   ```
   - Will verify Cursor CLI
   - Will prompt for login
   - Will request Todoist token

5. **Install Scheduler**:
   ```bash
   ./cronagent install
   ```

---

### For Existing Users

#### If You Have Cursor CLI Already:

✅ **No action needed!**
- Just update and continue using
- Setup will validate your installation

#### If You DON'T Have Cursor CLI:

⚠️ **Action Required:**

1. Install Cursor CLI (see steps above)
2. Run `cursor agent login`
3. Re-run setup: `./cronagent setup`
4. Reinstall scheduler: `./cronagent install`

---

## Configuration Changes

### .env.example (Before):

```bash
TODOIST_TOKEN=your_token_here
REFRESH_INTERVAL_SECONDS=300
USE_CURSOR_CLI=true  # ← REMOVED
CODE_LOCATION=~/personal/cron agent
```

### .env.example (After):

```bash
TODOIST_TOKEN=your_token_here
REFRESH_INTERVAL_SECONDS=300
CODE_LOCATION=~/personal/cron agent
```

**USE_CURSOR_CLI is gone** - CLI is always used!

---

## Troubleshooting

### "Cursor CLI not found" Error

**Problem**: Setup fails with Cursor CLI not found

**Solution**:
1. Install Cursor from https://cursor.sh
2. Enable CLI: `Cursor > Install 'cursor' command`
3. Verify: `which cursor` shows a path
4. Run setup again

---

### "Login failed" Error

**Problem**: Setup exits because Cursor login failed

**Solution**:
1. Try manual login: `cursor agent login`
2. Complete authentication in browser
3. Verify: `cursor agent status` shows "Logged in"
4. Run setup again

---

### "Empty response from Cursor CLI" in Logs

**Problem**: Tasks fail with empty CLI response

**Solution**:
1. Check Cursor authentication: `cursor agent status`
2. Re-login if needed: `cursor agent login`
3. Check Cursor CLI works: `cursor agent "test prompt"`
4. Increase timeout in code if needed

---

## Benefits of Mandatory CLI

### ✅ Consistent Experience
- All users get real AI responses
- No degraded fallback mode
- Predictable behavior

### ✅ Better Quality
- Real AI-powered task execution
- Context-aware responses
- No simple simulations

### ✅ Simpler Codebase
- No fallback logic to maintain
- Clearer error messages
- Easier to debug

### ✅ Forces Proper Setup
- Users install Cursor from start
- No confusion about modes
- Clear requirements

---

## What This Means for Development

### Code Structure

**Simplified**:
- No `use_cli` parameter
- No conditional CLI vs fallback logic
- One execution path only

**CursorAgent is now simpler**:
```python
def execute(self, task_content, task_id=None):
    """Execute task using Cursor AI CLI (REQUIRED)"""
    # Always uses CLI
    action_taken = self._execute_with_cli(task_content)
    return result
```

**No more fallback methods**:
- Deleted `_analyze_and_execute()`
- Deleted `_perform_calculation()`
- Removed simulation logic

### Error Handling

**All errors return error messages**:
```python
try:
    result = subprocess.run(cursor_cli_cmd, timeout=120)
    if result.returncode == 0:
        return result.stdout
    else:
        return f"❌ Error: {result.stderr}"  # No fallback!
except subprocess.TimeoutExpired:
    return f"❌ Error: CLI timeout"  # No fallback!
```

**User sees error in Todoist task comment**:
- Clear indication of what failed
- User can investigate and fix
- Better than silent fallback

---

## FAQ

### Q: What if Cursor CLI is down?

**A**: Tasks will fail with error messages. User must fix Cursor CLI to continue.

### Q: Can I use fallback mode for testing?

**A**: No, fallback mode was removed. Install Cursor CLI for testing.

### Q: What if I don't want to use Cursor AI?

**A**: This agent requires Cursor AI. Consider a different solution if you don't want AI execution.

### Q: Will old versions work?

**A**: Old commits still have fallback mode. But current main branch requires Cursor CLI.

### Q: Can I add fallback back?

**A**: You can, but it's not recommended. The agent is designed for AI execution.

---

## Testing the Change

### Verify Cursor CLI Requirement:

```bash
# 1. Temporarily hide Cursor CLI
mv /usr/local/bin/cursor /usr/local/bin/cursor.bak

# 2. Try to run setup
./cronagent setup

# Expected: Should fail with clear error message about Cursor CLI

# 3. Restore Cursor CLI
mv /usr/local/bin/cursor.bak /usr/local/bin/cursor

# 4. Run setup again
./cronagent setup

# Expected: Should validate CLI and prompt for login
```

### Verify Agent Behavior:

```bash
# 1. Complete setup with Cursor CLI
./cronagent setup

# 2. Install scheduler
./cronagent install

# 3. Create test task in Todoist
# Task: "Calculate 10 + 5"

# 4. Wait for execution (or trigger manually)
./cronagent

# 5. Check result in Todoist
# Expected: Real AI response (not "🧮 10 + 5 = 15" fallback)
```

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Cursor CLI** | Optional | **MANDATORY** |
| **Fallback mode** | Available | **REMOVED** |
| **Setup validation** | Warned if missing | **Exits if missing** |
| **Login requirement** | Skippable | **REQUIRED** |
| **Error handling** | Fallback on error | **Return error** |
| **USE_CURSOR_CLI** | Environment variable | **REMOVED** |
| **User experience** | Inconsistent (2 modes) | **Consistent (CLI only)** |

---

## Key Takeaway

**Cursor CLI is now the ONLY way the agent works.**

✅ Install Cursor  
✅ Enable CLI  
✅ Login during setup  
✅ Agent uses real AI  

❌ No fallback  
❌ No simulation  
❌ No local calculations  

**Quality over convenience!** 🚀

---

**Last Updated**: 2026-02-15  
**Breaking Change**: Yes - Requires Cursor CLI  
**Migration**: Install Cursor CLI, run setup

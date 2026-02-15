# Cursor CLI Integration

## Overview

The Cron Agent now integrates with **Cursor CLI** to execute tasks using real AI instead of simulation.

## How It Works

### 1. Task Flow

```
Todoist Task → Cron Agent → Cursor CLI → AI Response → Todoist Comment
```

1. **Task Detection**: Agent reads task from Todoist
2. **CLI Execution**: Task is sent to Cursor AI via `cursor agent --print`
3. **AI Processing**: Cursor AI processes the task and returns response
4. **Result Logging**: Response is logged to conversation logs
5. **Todoist Update**: Response is added as comment to the task
6. **Task Completion**: Task is marked as completed in Todoist

### 2. Configuration

#### Environment Variables

```bash
# .env file
USE_CURSOR_CLI=true   # Enable Cursor CLI (true/false)
```

- **`true`**: Uses real Cursor AI CLI (requires authentication)
- **`false`**: Uses fallback simulation mode

#### Cursor CLI Requirements

1. **Cursor must be installed** with CLI available at `~/.local/bin/cursor`
2. **User must be logged in**: Run `cursor agent login`
3. **Workspace context**: Agent runs in project directory

### 3. CLI Command Used

```bash
cursor agent \
  --print \                    # Non-interactive mode
  --trust \                     # Trust workspace without prompting
  --workspace /path/to/project \# Specify workspace
  --output-format text \       # Plain text output
  --force \                     # Force allow commands
  "Your task here"
```

### 4. Fallback Behavior

If Cursor CLI fails (timeout, error, not available), the agent automatically falls back to:

1. **Simple Calculations**: For math tasks (Hebrew/English)
   - Example: "Calculate 1000 × 20" → "🧮 1000 × 20 = 20000"

2. **Task Type Detection**: Basic categorization
   - Email tasks → "✉️ Email sent"
   - Report tasks → "📊 Report created"
   - Backup tasks → "💾 Backup completed"

3. **Generic Completion**: Default fallback
   - "✅ Task completed successfully"

## Examples

### Example 1: Calculation Task

**Todoist Task**: "Calculate 1000 × 20"

**With Cursor CLI**:
```
🤖 Cursor AI processing: Calculate 1000 × 20
   Using Cursor CLI...
   Workspace: /Users/aviad/personal/cron agent
   Timeout: 120 seconds
   ✅ Got response from Cursor AI (42 chars)

📥 Response: The result is 20,000
```

**Fallback Mode**:
```
📥 Response: 🧮 1000 × 20 = 20000
```

### Example 2: Code Task

**Todoist Task**: "Write a Python function to reverse a string"

**With Cursor CLI**:
```
📥 Response: 
def reverse_string(s: str) -> str:
    """Reverse a string."""
    return s[::-1]

# Example usage:
result = reverse_string("hello")  # returns "olleh"
```

**Fallback Mode**:
```
📥 Response: ✅ Task 'Write a Python function...' completed successfully
```

### Example 3: Question Task

**Todoist Task**: "What is the difference between Docker and VM?"

**With Cursor CLI**:
```
📥 Response:
Docker containers share the host OS kernel and are more lightweight,
while VMs include a full OS and hypervisor layer. Docker is faster
to start and uses less resources...
```

## Monitoring

### Check Cursor CLI Status

```bash
# Check if logged in
cursor agent status

# Test CLI manually
cursor agent --print "Hello, test"
```

### View Logs

Conversations are logged to:
- **`clean_logs/conversation_YYYY-MM-DD.log`**: Prompts and responses only
- **`logs/stdout.log`**: Full execution logs
- **`logs/stderr.log`**: Error logs

### Example Log Entry

```
==================================================
[2026-02-15 14:32:15] Task ID: 8234567890

📤 PROMPT:
Calculate 1000 × 20

📥 RESPONSE:
The result is 20,000

==================================================
```

## Troubleshooting

### Issue: Cursor CLI Timeout

**Symptom**: Tasks timeout after 120 seconds

**Solution**:
1. Check internet connection
2. Verify Cursor authentication: `cursor agent status`
3. Try simpler task to test
4. Check if Cursor API is down

### Issue: "Cursor CLI not found"

**Symptom**: Agent says CLI is not available

**Solution**:
1. Install Cursor CLI: `cursor agent install-shell-integration`
2. Verify installation: `which cursor`
3. Re-login: `cursor agent login`

### Issue: Empty Response

**Symptom**: CLI returns but response is empty

**Solution**:
- Agent automatically falls back to simulation
- Check if task is too complex or ambiguous
- Try rephrasing the task

### Issue: Permission Errors

**Symptom**: CLI fails with permission errors

**Solution**:
1. Run with `--force` flag (already enabled)
2. Trust workspace: `--trust` flag (already enabled)
3. Check workspace permissions

## Disabling Cursor CLI

To use only fallback simulation:

```bash
# .env file
USE_CURSOR_CLI=false
```

Or temporarily for testing:

```bash
USE_CURSOR_CLI=false python3 src/cron_agent.py
```

## Performance

| Mode | Response Time | Accuracy | Internet Required |
|------|---------------|----------|-------------------|
| Cursor CLI | 5-120s | High | Yes |
| Fallback | <1s | Limited | No |

## Security Notes

1. **Workspace Trust**: Agent runs with `--trust` flag to avoid prompts
2. **Command Execution**: CLI has access to all tools (`--force`)
3. **Authentication**: Uses your Cursor account authentication
4. **Data Privacy**: Tasks are sent to Cursor AI servers

## Advanced Configuration

### Custom Timeout

Modify timeout in `src/cron_agent.py`:

```python
timeout=120  # Change to desired seconds
```

### Custom Workspace

Agent uses current working directory by default. To override:

```python
workspace_path = "/path/to/custom/workspace"
```

### Model Selection

To use a specific model:

```bash
cursor agent --print --model gpt-5 "Your task"
```

(Not currently configured in agent, but can be added)

## Future Enhancements

Potential improvements:

1. **Model Selection**: Allow choosing AI model via .env
2. **Streaming Responses**: Stream partial responses in real-time
3. **Retry Logic**: Automatic retry on failure
4. **Response Caching**: Cache similar task responses
5. **Multi-turn Conversations**: Support follow-up questions

## Support

For issues with:
- **Cursor CLI**: See Cursor documentation
- **Cron Agent**: Check project README.md
- **Integration**: This document

---

**Last Updated**: 2026-02-15

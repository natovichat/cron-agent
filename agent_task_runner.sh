#!/bin/bash

# Agent Task Runner - Executes tasks from Google Tasks using Cursor CLI
# Runs every minute via LaunchAgent to check for and execute tasks
# Supports bulk execution: up to MAX_PARALLEL_TASKS tasks processed in parallel

set -e  # Exit on error

# Set environment variables for cron
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
export HOME="/Users/aviad.natovich"
export USER="aviad.natovich"
export SHELL="/bin/zsh"

# Configuration
GTCLI_EMAIL="natovichat@gmail.com"
TASK_LIST_ID="ejN6SzdoaVRBMG1oQm9CcQ"  # Agent tasks list
LOG_FILE="/Users/aviad.natovich/personal/cron agent/logs/agent_task_runner.log"
SUMMARY_LOG_FILE="/Users/aviad.natovich/personal/cron agent/logs/agent_task_runner_summary.log"
WORKSPACE_DIR="/Users/aviad.natovich/personal/rentApplication"
LOCK_FILE="/Users/aviad.natovich/personal/cron agent/.agent_task_runner.lock"
TASK_LOGS_DIR="/Users/aviad.natovich/personal/cron agent/task_logs"
MAX_PARALLEL_TASKS=4

# Logging function (detailed log)
log() {
    # Only echo to stdout - LaunchAgent plist will capture to log file
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Summary logging function (user-friendly log)
log_summary() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$SUMMARY_LOG_FILE"
}

# ──────────────────────────────────────────────
# Lock mechanism to prevent overlapping runs
# ──────────────────────────────────────────────
if [ -f "$LOCK_FILE" ]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
        log "Another instance is running (PID: $LOCK_PID). Skipping this run."
        exit 0
    else
        log "Stale lock file found (PID: $LOCK_PID no longer running). Removing."
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file with current PID
echo $$ > "$LOCK_FILE"

# Ensure lock file is removed on exit
cleanup() {
    rm -f "$LOCK_FILE"
    log "Lock file removed."
}
trap cleanup EXIT

log "========== Agent Task Runner Started (Parallel Mode: up to $MAX_PARALLEL_TASKS tasks) =========="
log_summary "=========================================="
log_summary "Agent Task Runner Started (Parallel Mode: up to $MAX_PARALLEL_TASKS tasks)"
log_summary "=========================================="

# Check if gtcli is available
if ! command -v gtcli &> /dev/null; then
    log "ERROR: gtcli not found. Please install gtcli first."
    exit 1
fi

# Check if cursor is available
if ! command -v cursor &> /dev/null; then
    log "ERROR: cursor CLI not found. Please install Cursor."
    exit 1
fi

# Ensure per-task log directory exists
mkdir -p "$TASK_LOGS_DIR"

# Get all uncompleted tasks from the Agent tasks list
log "Fetching tasks from Google Tasks..."
TASKS_OUTPUT=$(gtcli "$GTCLI_EMAIL" tasks "$TASK_LIST_ID" 2>&1)

if [ $? -ne 0 ]; then
    log "ERROR: Failed to fetch tasks: $TASKS_OUTPUT"
    exit 1
fi

# DEBUG: Log raw output
log "DEBUG: Raw tasks output:"
echo "$TASKS_OUTPUT" | while IFS= read -r line; do
    log "  $line"
done

# Parse up to MAX_PARALLEL_TASKS uncompleted tasks (status: ○)
# Exclude tasks already marked as in-progress (from a previous run that may still be executing)
UNCOMPLETED_TASKS=$(echo "$TASKS_OUTPUT" | grep "○" | grep -v "🔄 \[IN PROGRESS\]" | head -"$MAX_PARALLEL_TASKS")
TASK_COUNT=$(echo "$UNCOMPLETED_TASKS" | grep -c "○" 2>/dev/null || echo "0")

log "DEBUG: Found $TASK_COUNT uncompleted task(s) (max $MAX_PARALLEL_TASKS)"

if [ "$TASK_COUNT" -eq 0 ] || [ -z "$UNCOMPLETED_TASKS" ]; then
    log "No uncompleted tasks found. Nothing to do."
    log_summary "No uncompleted tasks. Waiting for next run..."
    log_summary ""
    exit 0
fi

log_summary ""
log_summary "📋 Found $TASK_COUNT task(s) to execute in parallel:"
log_summary ""

# ──────────────────────────────────────────────
# Build arrays of task IDs and titles
# ──────────────────────────────────────────────
declare -a TASK_IDS
declare -a TASK_TITLES
declare -a AGENT_PIDS
declare -a TASK_LOG_FILES

INDEX=0
while IFS= read -r task_line; do
    [ -z "$task_line" ] && continue
    
    TASK_IDS[$INDEX]=$(echo "$task_line" | cut -f1)
    TASK_TITLES[$INDEX]=$(echo "$task_line" | cut -f3)
    
    log "  Task $((INDEX+1)): [${TASK_IDS[$INDEX]}] ${TASK_TITLES[$INDEX]}"
    log_summary "  $((INDEX+1)). ${TASK_TITLES[$INDEX]}"
    
    INDEX=$((INDEX + 1))
done <<< "$UNCOMPLETED_TASKS"

TOTAL_TASKS=$INDEX
log ""
log "Preparing to execute $TOTAL_TASKS task(s) in parallel..."

# Check cursor agent authentication before running
log "Checking cursor agent status..."
cursor agent status >> "$LOG_FILE" 2>&1
AUTH_CHECK_EXIT=$?
log "Cursor agent status exit code: $AUTH_CHECK_EXIT"

if [ $AUTH_CHECK_EXIT -ne 0 ]; then
    log "WARNING: Cursor agent may not be authenticated"
fi

# ──────────────────────────────────────────────
# Function: Mark task as in-progress in Google Tasks
# ──────────────────────────────────────────────
mark_task_in_progress() {
    local task_id=$1
    local task_title=$2
    local in_progress_title="🔄 [IN PROGRESS] $task_title"
    
    log "  📝 Marking task as in-progress: $task_title"
    gtcli "$GTCLI_EMAIL" tasks "$TASK_LIST_ID" update "$task_id" --title "$in_progress_title" 2>&1
    if [ $? -eq 0 ]; then
        log "  ✅ Task title updated to indicate in-progress"
    else
        log "  ⚠️  Failed to update task title (non-critical, continuing...)"
    fi
}

# ──────────────────────────────────────────────
# Function: Restore original task title (remove in-progress indicator)
# ──────────────────────────────────────────────
restore_task_title() {
    local task_id=$1
    local original_title=$2
    
    log "  📝 Restoring original task title: $original_title"
    gtcli "$GTCLI_EMAIL" tasks "$TASK_LIST_ID" update "$task_id" --title "$original_title" 2>&1
    if [ $? -eq 0 ]; then
        log "  ✅ Task title restored to original"
    else
        log "  ⚠️  Failed to restore task title (non-critical)"
    fi
}

# ──────────────────────────────────────────────
# Function: Execute a single task via Cursor Agent
# ──────────────────────────────────────────────
execute_task() {
    local task_index=$1
    local task_id=$2
    local task_title=$3
    local task_log_file=$4
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== Sub-Agent $((task_index+1)) Started ==========" >> "$task_log_file"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task: $task_title" >> "$task_log_file"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task ID: $task_id" >> "$task_log_file"
    
    # Create system prompt for this specific task
    local system_prompt="You are an autonomous AI agent executing a task from the user's Google Tasks list.

TASK TO EXECUTE: $task_title

INSTRUCTIONS:
- Execute this task completely and autonomously
- Use ALL available tools, skills, and commands at your disposal
- Use the browser for any web-based tasks
- Use GitLab CLI (glab) for any GitLab operations
- Use gtcli for Google Tasks operations
- Use send_email.py for email notifications
- Use Cursor commands (like /send-mr-link) when appropriate
- Access and use all MCP servers available
- Read any necessary files and documentation
- Make code changes if needed
- Run tests and verify results
- After completing the task successfully, mark it as complete using:
  gtcli $GTCLI_EMAIL tasks $TASK_LIST_ID complete $task_id

AVAILABLE RESOURCES:
- Skills directory: ~/.cursor/skills/
- Commands: /send-mr-link, and others
- MCP servers: Gmail, Jira, Browser
- GitLab: glab CLI
- Google Tasks: gtcli
- Email: /Users/aviad.natovich/Code/Tasks/Tools/send_email.py

ANSWER FORMAT (MANDATORY):
Before marking the task as complete, you MUST write a short formatted answer back to the Google Task notes.
Use this exact command to update the task with your answer:
  gtcli $GTCLI_EMAIL tasks $TASK_LIST_ID update $task_id --notes \"<your formatted answer>\"

The answer MUST follow this format:
---
✅ Status: <Success/Partial/Failed>
📋 Answer: <1-3 sentence summary of the result or answer>
🔧 Actions: <comma-separated list of key actions taken>
📅 Completed: <current date and time>
---

Example answer notes:
---
✅ Status: Success
📋 Answer: MR link sent to Regev on Slack for airflow3 repo, MR #142 (feature/update-dags).
🔧 Actions: glab mr list, /send-mr-link, Slack message
📅 Completed: 2026-02-13 09:30
---

Keep the answer SHORT and CONCISE (max 4 lines). This is meant to be a quick glanceable summary.

WORKFLOW:
1. Analyze the task thoroughly
2. Break it down into steps if needed
3. Execute each step using appropriate tools
4. Verify completion
5. Write the short formatted answer to the Google Task notes (MANDATORY - see ANSWER FORMAT above)
6. Mark task as complete in Google Tasks
7. Send a summary of what you did via email to natovichat@gmail.com using:
   python3 /Users/aviad.natovich/Code/Tasks/Tools/send_email.py -s \"Cron Agent Task Complete: \$(echo $task_title | head -c 50)\" -b \"<summary of actions taken and results>\" -t natovichat@gmail.com
   The email body should include: task name, what was done, tools used, and final status (success/failure).
8. Play completion sound: afplay /System/Library/Sounds/Glass.aiff

Execute the task now with full autonomy!"

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting cursor agent execution..." >> "$task_log_file"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ==================== CURSOR AGENT OUTPUT START ====================" >> "$task_log_file"
    
    # Run cursor agent and capture output to per-task log
    cursor agent \
      --print \
      --output-format stream-json \
      --stream-partial-output \
      --workspace "$WORKSPACE_DIR" \
      --approve-mcps \
      --force \
      "$system_prompt" 2>&1 | while IFS= read -r line; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] AGENT: $line" >> "$task_log_file"
        
        # Parse JSON to extract tool usage
        if echo "$line" | grep -q '"type":"tool_use"'; then
            tool_name=$(echo "$line" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
            if [ ! -z "$tool_name" ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔧 TOOL USED: $tool_name" >> "$task_log_file"
            fi
        fi
        
        # Extract skill usage
        if echo "$line" | grep -q -i "skill"; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📚 SKILL MENTIONED: $line" >> "$task_log_file"
        fi
        
        # Extract command usage
        if echo "$line" | grep -q "^/[a-z]"; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚡ COMMAND: $line" >> "$task_log_file"
        fi
    done
    
    local exit_code=${PIPESTATUS[0]}
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ==================== CURSOR AGENT OUTPUT END ====================" >> "$task_log_file"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cursor agent finished with exit code: $exit_code" >> "$task_log_file"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========== Sub-Agent $((task_index+1)) Finished ==========" >> "$task_log_file"
    
    return $exit_code
}

# ──────────────────────────────────────────────
# Launch all tasks in parallel
# ──────────────────────────────────────────────
RUN_TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
log ""
log "🚀 Launching $TOTAL_TASKS sub-agent(s) in parallel..."
log_summary ""
log_summary "🚀 Launching $TOTAL_TASKS sub-agent(s) in parallel..."
log_summary "──────────────────────────────────"

for i in $(seq 0 $((TOTAL_TASKS - 1))); do
    TASK_LOG_FILES[$i]="$TASK_LOGS_DIR/task_${RUN_TIMESTAMP}_$((i+1))_${TASK_IDS[$i]}.log"
    
    log "  🤖 Sub-Agent $((i+1)): '${TASK_TITLES[$i]}'"
    log "     Log: ${TASK_LOG_FILES[$i]}"
    log_summary "  🤖 Sub-Agent $((i+1)): ${TASK_TITLES[$i]}"
    
    # Mark task as in-progress in Google Tasks before launching
    mark_task_in_progress "${TASK_IDS[$i]}" "${TASK_TITLES[$i]}"
    
    # Launch task execution in background
    execute_task "$i" "${TASK_IDS[$i]}" "${TASK_TITLES[$i]}" "${TASK_LOG_FILES[$i]}" &
    AGENT_PIDS[$i]=$!
    
    log "  ↳ PID: ${AGENT_PIDS[$i]}"
    
    # Small delay between launches to avoid resource contention
    sleep 2
done

log ""
log "All $TOTAL_TASKS sub-agents launched. PIDs: ${AGENT_PIDS[*]}"
log "Waiting for all sub-agents to complete..."

# ──────────────────────────────────────────────
# Wait for all parallel tasks to complete
# ──────────────────────────────────────────────
declare -a EXIT_CODES
for i in $(seq 0 $((TOTAL_TASKS - 1))); do
    wait "${AGENT_PIDS[$i]}" 2>/dev/null
    EXIT_CODES[$i]=$?
    
    if [ ${EXIT_CODES[$i]} -eq 0 ]; then
        log "  ✅ Sub-Agent $((i+1)) (PID ${AGENT_PIDS[$i]}) completed successfully"
    else
        log "  ⚠️  Sub-Agent $((i+1)) (PID ${AGENT_PIDS[$i]}) exited with code: ${EXIT_CODES[$i]}"
        # Restore original title for failed tasks so they don't stay stuck with in-progress indicator
        restore_task_title "${TASK_IDS[$i]}" "${TASK_TITLES[$i]}"
    fi
done

log ""
log "All sub-agents have finished."

# ──────────────────────────────────────────────
# Generate execution summary per task
# ──────────────────────────────────────────────
log ""
log "========== Execution Summary =========="
log_summary ""
log_summary "──────────────────────────────────"
log_summary "📊 Execution Results:"

for i in $(seq 0 $((TOTAL_TASKS - 1))); do
    log ""
    log "--- Task $((i+1)): ${TASK_TITLES[$i]} ---"
    
    if [ ${EXIT_CODES[$i]} -eq 0 ]; then
        log "  Status: ✅ Success (exit code 0)"
        log_summary "  ✅ Task $((i+1)): ${TASK_TITLES[$i]} - Success"
    else
        log "  Status: ⚠️  Issues (exit code ${EXIT_CODES[$i]})"
        log_summary "  ⚠️  Task $((i+1)): ${TASK_TITLES[$i]} - Exit code ${EXIT_CODES[$i]}"
    fi
    
    # Extract tool usage from per-task log
    if [ -f "${TASK_LOG_FILES[$i]}" ]; then
        TOOLS_USED=$(grep "🔧 TOOL USED:" "${TASK_LOG_FILES[$i]}" | awk -F': ' '{print $NF}' | sort -u)
        if [ ! -z "$TOOLS_USED" ]; then
            log "  Tools used:"
            echo "$TOOLS_USED" | while read tool; do
                log "    - $tool"
            done
        fi
    fi
    
    log "  Log: ${TASK_LOG_FILES[$i]}"
done

log "========================================"

# ──────────────────────────────────────────────
# Verification Phase: Check all tasks
# ──────────────────────────────────────────────
log ""
log "========== Verification Phase =========="
log "Checking if tasks were marked complete in Google Tasks..."
log_summary ""
log_summary "🔍 Verification:"

VERIFICATION_OUTPUT=$(gtcli "$GTCLI_EMAIL" tasks "$TASK_LIST_ID" 2>&1)

COMPLETED_COUNT=0
INCOMPLETE_COUNT=0

for i in $(seq 0 $((TOTAL_TASKS - 1))); do
    task_id="${TASK_IDS[$i]}"
    task_title="${TASK_TITLES[$i]}"
    
    if echo "$VERIFICATION_OUTPUT" | grep -q "$task_id"; then
        TASK_STATUS=$(echo "$VERIFICATION_OUTPUT" | grep "$task_id" | cut -f2)
        if [ "$TASK_STATUS" = "●" ]; then
            log "  ✅ Task $((i+1)): VERIFIED complete (●) - $task_title"
            log_summary "  ✅ Task $((i+1)): Verified complete"
            COMPLETED_COUNT=$((COMPLETED_COUNT + 1))
        elif [ "$TASK_STATUS" = "○" ]; then
            log "  ⚠️  Task $((i+1)): Still INCOMPLETE (○) - $task_title"
            log_summary "  ⚠️  Task $((i+1)): Still incomplete"
            INCOMPLETE_COUNT=$((INCOMPLETE_COUNT + 1))
        fi
    else
        log "  ❓ Task $((i+1)): Not found in list - $task_title"
        log_summary "  ✅ Task $((i+1)): Removed from list (likely completed)"
        COMPLETED_COUNT=$((COMPLETED_COUNT + 1))
    fi
done

log ""
log "Verification Summary: $COMPLETED_COUNT completed, $INCOMPLETE_COUNT incomplete out of $TOTAL_TASKS total"

log "========== Agent Task Runner Finished =========="
log ""

log_summary ""
log_summary "📊 Final: $COMPLETED_COUNT/$TOTAL_TASKS tasks completed"
log_summary "=========================================="
log_summary ""

# ──────────────────────────────────────────────
# Send summary log via email
# ──────────────────────────────────────────────
log "Sending summary log via email to natovichat@gmail.com..."
SUMMARY_CONTENT=$(cat "$SUMMARY_LOG_FILE" 2>/dev/null || echo "No summary available")
EMAIL_SUBJECT="Cron Agent Summary - $(date '+%Y-%m-%d %H:%M') - $COMPLETED_COUNT/$TOTAL_TASKS completed"

python3 /Users/aviad.natovich/Code/Tasks/Tools/send_email.py \
    -s "$EMAIL_SUBJECT" \
    -b "$SUMMARY_CONTENT" \
    -t "natovichat@gmail.com" 2>&1

if [ $? -eq 0 ]; then
    log "✅ Summary email sent successfully"
else
    log "⚠️  Failed to send summary email"
fi

exit 0

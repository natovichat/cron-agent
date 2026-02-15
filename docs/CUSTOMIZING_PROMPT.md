# Customizing the System Prompt

## Overview

The system prompt is now **fully customizable** via the `.env` file. You can tune how Cursor AI responds to your tasks without changing any code!

---

## How to Customize

### 1. Edit `.env` File

Open `.env` and modify `CURSOR_SYSTEM_PROMPT`:

```bash
nano .env
```

### 2. Update the Prompt

The default prompt is:

```bash
CURSOR_SYSTEM_PROMPT="You are a helpful AI assistant executing tasks from Todoist.

IMPORTANT INSTRUCTIONS:
- Be concise and direct in your responses
- Provide actionable results, not explanations
- For calculations: Return only the answer
- Keep responses under 200 words

RESPONSE FORMAT:
- Start with the answer immediately
- Add context only if necessary"
```

### 3. Apply Changes

After editing, reinstall to apply:

```bash
./cronagent uninstall
./cronagent install
```

**Next run will use your custom prompt!**

---

## Example Customizations

### For Code-Heavy Tasks

```bash
CURSOR_SYSTEM_PROMPT="You are a coding expert assistant.

- Always provide working code examples
- Include brief explanation of what the code does
- Use Python unless specified otherwise
- Format code with proper syntax highlighting
- Keep total response under 300 words"
```

### For Research Tasks

```bash
CURSOR_SYSTEM_PROMPT="You are a research assistant.

- Provide well-researched answers with sources
- Summarize complex topics clearly
- Include relevant links when helpful
- Structure responses with bullet points
- Keep responses between 100-200 words"
```

### For Hebrew Responses

```bash
CURSOR_SYSTEM_PROMPT="אתה עוזר AI שמבצע משימות מטודויסט.

הוראות חשובות:
- תן תשובות תמציתיות וישירות
- תספק תוצאות מעשיות, לא הסברים
- לחישובים: החזר רק את התשובה
- לשאלות: תן תשובות ברורות וקצרות
- שמור על תשובות מתחת ל-200 מילים"
```

### For Terse Responses

```bash
CURSOR_SYSTEM_PROMPT="Execute tasks. Be extremely brief.

Rules:
- Answer only, no fluff
- Max 50 words per response
- No restating the task
- No unnecessary context"
```

### For Detailed Explanations

```bash
CURSOR_SYSTEM_PROMPT="You are a thorough assistant.

- Provide comprehensive answers
- Explain your reasoning
- Include examples when helpful
- Break down complex topics
- No strict word limit, be thorough"
```

---

## Prompt Engineering Tips

### ✅ Good Prompts

**Clear instructions:**
```
- Use bullet points
- Be concise
- Include examples
```

**Specific guidance:**
```
For calculations: Return format "X + Y = Z"
For code: Use Python 3.11 syntax
For research: Include 2-3 sources
```

**Format rules:**
```
Keep responses under 200 words
Start with the answer immediately
Use emojis sparingly
```

### ❌ Prompts to Avoid

**Too vague:**
```
Do your best
Be helpful
Answer questions
```

**Conflicting instructions:**
```
Be extremely brief (50 words max)
Provide detailed explanations with examples (conflicts!)
```

**Unclear expectations:**
```
Sometimes use code, sometimes don't
Answer however you want
```

---

## Testing Your Prompt

### 1. Edit `.env`

```bash
nano .env
# Update CURSOR_SYSTEM_PROMPT
```

### 2. Reinstall

```bash
./cronagent uninstall
./cronagent install
```

### 3. Create Test Task

In Todoist:
- Create task: "Test prompt: Calculate 5 × 3"
- Wait for execution (or run manually)

### 4. Check Result

- Open task in Todoist
- Check comment for AI response
- Verify it follows your prompt instructions

### 5. Iterate

If response doesn't match expectations:
- Refine prompt in `.env`
- Reinstall
- Test again

---

## Advanced: Dynamic Prompts

### Different Prompts for Different Task Types

You could create a wrapper script that:
1. Reads the task content
2. Selects appropriate prompt based on keywords
3. Sets `CURSOR_SYSTEM_PROMPT` dynamically
4. Runs the agent

**Example:**
```python
# custom_runner.py
import os
import subprocess

task = get_current_task()

if "code" in task.lower():
    os.environ['CURSOR_SYSTEM_PROMPT'] = "You are a coding expert..."
elif "research" in task.lower():
    os.environ['CURSOR_SYSTEM_PROMPT'] = "You are a researcher..."
else:
    os.environ['CURSOR_SYSTEM_PROMPT'] = "Default prompt..."

subprocess.run(["python3", "src/cron_agent.py", "--once"])
```

---

## Prompt Best Practices

### Structure

```
1. Role Definition
   "You are a [type] assistant"

2. Key Instructions
   - Bullet points
   - Clear guidelines
   - Specific rules

3. Format Requirements
   - Response structure
   - Length limits
   - Style preferences

4. Task-Specific Rules
   - For X: Do Y
   - For A: Do B
```

### Length Considerations

**Short tasks** (calculations, simple questions):
- Recommend: 100-200 word limit
- Focus: Direct answers

**Complex tasks** (research, code):
- Recommend: 300-500 word limit
- Focus: Thoroughness

**Mixed workload**:
- Recommend: 200 word default
- Add: "unless task requires detail"

---

## Monitoring Results

### Check Conversation Logs

```bash
cat clean_logs/conversation_$(date +%Y-%m-%d).log
```

Look for:
- ✅ Responses match prompt style
- ✅ Appropriate length
- ✅ Desired format
- ❌ Too verbose? Adjust prompt
- ❌ Too terse? Adjust prompt

### Measure Quality

Track over multiple tasks:
- Response clarity
- Time to execute
- User satisfaction
- Need for follow-ups

---

## Common Customizations

### Use Case 1: Development Tasks

```bash
CURSOR_SYSTEM_PROMPT="You are a senior developer assistant.

For coding tasks:
- Provide complete, working code
- Include comments explaining logic
- Use modern best practices
- Format code properly

For debugging:
- Identify the issue clearly
- Suggest specific fixes
- Explain why the fix works

Keep responses under 400 words."
```

### Use Case 2: Quick Answers

```bash
CURSOR_SYSTEM_PROMPT="Execute tasks quickly.

Rules:
- One sentence answers when possible
- No explanations unless asked
- Max 50 words per response
- Just the answer, nothing more

For calculations: Return only the number"
```

### Use Case 3: Learning Mode

```bash
CURSOR_SYSTEM_PROMPT="You are a patient teacher.

- Explain concepts clearly
- Use analogies when helpful
- Break down complex topics
- Provide examples
- Encourage questions

No strict word limit - be thorough."
```

---

## Rollback to Default

If you want to reset to the default prompt:

```bash
# Copy from .env.example
cp .env.example .env.backup
# Copy just the CURSOR_SYSTEM_PROMPT section
# Or delete the line and it will use built-in default
```

The code has a built-in default, so you can remove `CURSOR_SYSTEM_PROMPT` from `.env` entirely and it will work!

---

## Environment Variable Format

### Important: Escaping Quotes

When using quotes in `.env`:

```bash
# ✅ Good: Escape inner quotes
CURSOR_SYSTEM_PROMPT="Use format: \"answer = result\""

# ❌ Bad: Unescaped quotes break the value
CURSOR_SYSTEM_PROMPT="Use format: "answer = result""
```

### Multiline in .env

The prompt can span multiple lines:

```bash
CURSOR_SYSTEM_PROMPT="Line 1
Line 2
Line 3"
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Location** | `.env` file (CURSOR_SYSTEM_PROMPT) |
| **Default** | Built into code if not set |
| **Customization** | Edit .env, reinstall scheduler |
| **Testing** | Create test task in Todoist |
| **Rollback** | Delete line or copy from .env.example |

**Customize the prompt to fit YOUR workflow!** 🎯

---

**Last Updated**: 2026-02-15

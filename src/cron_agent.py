#!/usr/bin/env python3
"""
Cron Agent - Smart Task Automation
===================================

System that schedules recurring tasks, reads tasks from Todoist,
sends them to Cursor AI for execution, and updates results back.

Author: Your Name
Date: 2025-02-15
"""

import os
import time
import schedule
import requests
import subprocess
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class CleanLogger:
    """
    Clean logger that shows only prompts and responses, without debug info
    """
    
    def __init__(self, log_dir: str = "clean_logs"):
        """
        Initialize the logger
        
        Args:
            log_dir: Directory to save logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create filename with date
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"conversation_{today}.log"
    
    def log_conversation(self, prompt: str, response: str, task_id: str = None):
        """
        Log conversation to clean log
        
        Args:
            prompt: The prompt we sent
            response: The response we received
            task_id: Task ID (optional)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"""
{'='*70}
[{timestamp}]{f' Task ID: {task_id}' if task_id else ''}

📤 PROMPT:
{prompt}

📥 RESPONSE:
{response}

{'='*70}

"""
        
        # Write to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def get_log_file_path(self) -> str:
        """
        Get file path
        
        Returns:
            File path
        """
        return str(self.log_file)


class TodoistAPI:
    """
    Interface for working with Todoist API
    """
    
    def __init__(self, token: str):
        """
        Initialize the API
        
        Args:
            token: API Token from Todoist
        """
        self.token = token
        # Updated to use new Todoist API v1 (migrated from REST API v2)
        self.base_url = "https://api.todoist.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def validate_token(self) -> bool:
        """
        Validate that the Todoist API token is valid by testing the API connection.
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Test the token by fetching tasks (always available endpoint)
            url = f"{self.base_url}/tasks"
            
            # Debug: print what we're testing
            print(f"   Testing: {url}")
            print(f"   Token length: {len(self.token)} chars")
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✓ API connection successful")
                return True
            elif response.status_code == 401:
                print(f"❌ Authentication failed: Invalid Todoist API token")
                print(f"   Status code: {response.status_code}")
                print(f"   This usually means the token is wrong or expired")
                return False
            elif response.status_code == 403:
                print(f"❌ Access forbidden: Token doesn't have required permissions")
                print(f"   Status code: {response.status_code}")
                return False
            elif response.status_code == 410:
                print(f"❌ API endpoint no longer available (410 Gone)")
                print(f"   URL tested: {url}")
                print(f"   This might indicate:")
                print(f"   - The token format has changed")
                print(f"   - Your account has issues")
                print(f"   - The API has been updated")
                print(f"\n   Response body: {response.text[:300]}")
                return False
            else:
                print(f"❌ Unexpected response from Todoist API")
                print(f"   Status code: {response.status_code}")
                print(f"   Response: {response.text[:300]}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"❌ Connection timeout: Could not reach Todoist API")
            print(f"   Check your internet connection")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error: Could not connect to Todoist API")
            print(f"   Error: {e}")
            print(f"   Check your internet connection")
            return False
        except Exception as e:
            print(f"❌ Error validating Todoist token: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_tasks(self) -> List[Dict]:
        """
        Get all active tasks
        
        Returns:
            List of tasks
        """
        try:
            response = requests.get(
                f"{self.base_url}/tasks",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            # New API v1 returns {results: [...]} format
            tasks = data.get('results', []) if isinstance(data, dict) else data
            
            # Filter incomplete tasks (new API uses 'checked' instead of 'is_completed')
            active_tasks = [t for t in tasks if not t.get('checked', False)]
            
            print(f"📋 Found {len(active_tasks)} active tasks")
            return active_tasks
            
        except Exception as e:
            print(f"❌ Error fetching tasks: {e}")
            return []
    
    def complete_task(self, task_id: str) -> bool:
        """
        Mark task as completed
        
        Args:
            task_id: Task ID
            
        Returns:
            Whether the operation succeeded
        """
        try:
            # New API v1 uses /tasks/{id}/close endpoint
            response = requests.post(
                f"{self.base_url}/tasks/{task_id}/close",
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Error completing task {task_id}: {e}")
            return False
    
    def add_comment(self, task_id: str, comment: str) -> bool:
        """
        Add comment to task
        
        Args:
            task_id: Task ID
            comment: Comment content
            
        Returns:
            Whether the operation succeeded
        """
        try:
            # New API v1 uses top-level /comments endpoint with task_id in body
            response = requests.post(
                f"{self.base_url}/comments",
                headers=self.headers,
                json={
                    "task_id": task_id,
                    "content": comment
                }
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return False


class CursorAgent:
    """
    Cursor AI Agent using Cursor CLI (REQUIRED)
    """
    
    DEFAULT_CODE_LOCATION = "~/personal/cron agent"
    
    def __init__(
        self,
        clean_logger: CleanLogger = None,
        code_location: Optional[str] = None,
    ):
        """
        Initialize Cursor Agent
        
        Args:
            clean_logger: Logger for conversations
            code_location: Path to the codebase for Cursor context
        """
        self.execution_log = []
        self.clean_logger = clean_logger
        self.code_location = code_location or os.getenv(
            "CODE_LOCATION", self.DEFAULT_CODE_LOCATION
        )
        self.cursor_cli_path = self._find_cursor_cli()
        
        # Validate Cursor CLI is available
        if not self.cursor_cli_path:
            print()
            print("❌ FATAL ERROR: Cursor CLI is required but not found!")
            print()
            print("Installation Instructions:")
            print("1. Visit: https://cursor.sh")
            print("2. Download and install Cursor")
            print("3. Enable CLI: Cursor > Install 'cursor' command")
            print()
            print("After installing, run setup again: ./cronagent setup")
            print()
            sys.exit(1)
    
    def _find_cursor_cli(self) -> Optional[str]:
        """
        Find Cursor CLI executable (REQUIRED)
        
        Returns:
            Path to cursor CLI or None if not found
        """
        try:
            result = subprocess.run(
                ["which", "cursor"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                path = result.stdout.strip()
                print(f"✅ Found Cursor CLI: {path}")
                return path
            else:
                return None
        except Exception as e:
            print(f"⚠️  Error finding Cursor CLI: {e}")
            return None
    
    def execute(self, task_content: str, task_id: str = None) -> Dict[str, any]:
        """
        Execute task using Cursor AI CLI
        
        Args:
            task_content: Task description
            task_id: Task ID (for logging)
            
        Returns:
            Execution result
        """
        print(f"🤖 Cursor AI processing: {task_content}")
        
        start_time = time.time()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Execute with Cursor CLI
        action_taken = self._execute_with_cli(task_content)
        
        duration = time.time() - start_time
        
        # Check if execution was successful (no error message)
        success = not action_taken.startswith("❌ Error:")
        
        result = {
            "success": success,
            "task": task_content,
            "timestamp": timestamp,
            "action_taken": action_taken,
            "duration": f"{duration:.2f}s"
        }
        
        # Write to clean log (only prompt and response)
        if self.clean_logger:
            self.clean_logger.log_conversation(
                prompt=task_content,
                response=action_taken,
                task_id=task_id
            )
        
        self.execution_log.append(result)
        return result
    
    def _format_prompt(self, task_content: str) -> str:
        """
        Format the prompt with system instructions for optimal Cursor AI execution.
        
        Args:
            task_content: Original task content from Todoist
            
        Returns:
            Formatted prompt with system instructions and task
        """
        # Default system prompt (used if not in .env)
        default_system_prompt = """You are an autonomous AI agent executing a task from the user's Todoist list.

INSTRUCTIONS:
- Execute this task completely and autonomously
- Use ALL available tools, skills, and commands at your disposal
- For calculations: Compute and return ONLY the answer (e.g., "56" or "The answer is 56")
- For questions: Provide clear, brief answers (1-3 sentences max)
- For code tasks: Make changes, run tests, verify results
- For web tasks: Use browser tools
- Access and use all MCP servers available (Gmail, Jira, etc.)

RESPONSE FORMAT (MANDATORY):
- Start with the direct answer/result immediately
- Keep responses SHORT and CONCISE (max 3-4 lines)
- For calculations: Just the number or "The answer is X"
- No explanations of what you plan to do - just do it and report the result

"""
        
        # Get system prompt from environment (allows customization)
        system_prompt = os.getenv('CURSOR_SYSTEM_PROMPT', default_system_prompt)
        
        return system_prompt + f"\nTASK:\n{task_content}"
    
    def _parse_stream_json_output(self, output: str) -> str:
        """
        Parse stream-json format output from Cursor CLI.
        
        Extracts text content from JSON events.
        
        Args:
            output: Raw stream-json output
            
        Returns:
            Extracted text response
        """
        if not output:
            return ""
        
        import json
        text_parts = []
        
        # Process each line as separate JSON event
        for line in output.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            try:
                event = json.loads(line)
                
                # Extract text from text content blocks
                if event.get('type') == 'content_block_delta':
                    delta = event.get('delta', {})
                    if delta.get('type') == 'text_delta':
                        text = delta.get('text', '')
                        if text:
                            text_parts.append(text)
                
                # Also check for direct text in content blocks
                elif event.get('type') == 'text':
                    text = event.get('text', '')
                    if text:
                        text_parts.append(text)
                        
            except json.JSONDecodeError:
                # Skip non-JSON lines (debug output, etc.)
                continue
        
        return ''.join(text_parts).strip()
    
    def _execute_with_cli(self, task_content: str) -> str:
        """
        Execute task using Cursor CLI
        
        Args:
            task_content: Task to execute
            
        Returns:
            Response from Cursor AI
        """
        try:
            print("   Using Cursor CLI...")
            
            # Resolve code location to absolute path for workspace
            expanded_location = os.path.expanduser(self.code_location)
            workspace_path = str(Path(expanded_location).resolve())
            
            # Format the prompt with code location context
            formatted_prompt = self._format_prompt(task_content)
            
            # Run cursor agent with streaming JSON output (proven to work in background)
            cmd = [
                self.cursor_cli_path,
                "agent",
                "--print",
                "--output-format", "stream-json",  # Critical: stream-json works in background
                "--stream-partial-output",  # Critical: enables streaming
                "--workspace", workspace_path,
                "--approve-mcps",  # Auto-approve MCP servers
                formatted_prompt,
            ]
            
            print(f"   Code location: {self.code_location}")
            print(f"   Workspace: {workspace_path}")
            print(f"   Timeout: 120 seconds")
            
            # Capture all output
            full_response = []
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 120 second timeout (2 minutes)
                check=False,
                cwd=workspace_path  # Run in workspace directory
            )
            
            # Parse streaming JSON output to extract the actual response
            response_text = self._parse_stream_json_output(result.stdout)
            
            if result.returncode == 0 and response_text:
                print(f"   ✅ Got response from Cursor AI ({len(response_text)} chars)")
                return response_text
            elif not response_text:
                error_msg = "Empty response from Cursor CLI"
                print(f"   ❌ {error_msg}")
                if result.stderr:
                    print(f"   stderr: {result.stderr[:200]}")
                return f"❌ Error: {error_msg}"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                print(f"   ❌ Cursor CLI error (code {result.returncode}): {error_msg[:200]}")
                return f"❌ Error: {error_msg[:200]}"
        
        except subprocess.TimeoutExpired:
            error_msg = "Cursor CLI timeout (>120s)"
            print(f"   ❌ {error_msg}")
            return f"❌ Error: {error_msg}"
        except Exception as e:
            error_msg = f"Error running Cursor CLI: {e}"
            print(f"   ❌ {error_msg}")
            return f"❌ Error: {error_msg}"


class CronAgent:
    """
    Main engine of the system - schedules and executes tasks
    """
    
    def __init__(
        self,
        todoist_token: str,
        clean_log_dir: str = "clean_logs",
        code_location: Optional[str] = None,
    ):
        """
        Initialize the Cron Agent
        
        Args:
            todoist_token: Todoist API Token
            clean_log_dir: Directory for clean log
            code_location: Path to the codebase for Cursor context
        """
        self.todoist = TodoistAPI(todoist_token)
        self.clean_logger = CleanLogger(clean_log_dir)
        self.cursor = CursorAgent(
            clean_logger=self.clean_logger,
            code_location=code_location,
        )
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "start_time": datetime.now()
        }
        
        # Print clean log location
        print(f"📝 Clean log saved to: {self.clean_logger.get_log_file_path()}")
    
    def process_tasks(self):
        """
        Process all active tasks
        """
        print("\n" + "="*50)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # Get tasks
        tasks = self.todoist.get_tasks()
        
        if not tasks:
            print("💤 No new tasks to process")
            return
        
        # Process each task
        for task in tasks:
            self._process_single_task(task)
        
        # Show statistics
        self._print_stats()
    
    def _process_single_task(self, task: Dict):
        """
        Process a single task
        
        Args:
            task: Task object
        """
        task_id = task['id']
        task_content = task['content']
        
        print(f"\n📝 Processing task: {task_content}")
        
        try:
            # Execute task in Cursor
            result = self.cursor.execute(task_content, task_id=task_id)
            
            # Update in Todoist with the actual response
            comment = f"""
🎯 Execution Result:
- Status: {"✅ Success" if result['success'] else "❌ Failed"}
- Answer: {result['action_taken'][:200]}
- Time: {result['timestamp']}
- Duration: {result['duration']}
"""
            
            self.todoist.add_comment(task_id, comment)
            self.todoist.complete_task(task_id)
            
            # Update statistics
            self.stats['total_processed'] += 1
            if result['success']:
                self.stats['successful'] += 1
                print(f"✅ Task completed: {result['action_taken'][:100]}")
            else:
                self.stats['failed'] += 1
                print(f"❌ Task failed: {result['action_taken'][:100]}")
            
        except Exception as e:
            print(f"❌ Error processing task: {e}")
            self.stats['failed'] += 1
    
    def _print_stats(self):
        """
        Display statistics
        """
        uptime = datetime.now() - self.stats['start_time']
        
        print("\n" + "-"*50)
        print("📊 Statistics:")
        print(f"   🎯 Total tasks: {self.stats['total_processed']}")
        print(f"   ✅ Successful: {self.stats['successful']}")
        print(f"   ❌ Failed: {self.stats['failed']}")
        print(f"   ⏱️  Uptime: {str(uptime).split('.')[0]}")
        print("-"*50)
    
    def run_once(self):
        """
        Run the agent once and exit.
        
        Used when running via OS scheduler (LaunchAgent/systemd/cron).
        OS handles the scheduling, script just processes and exits.
        """
        print("🚀 Cron Agent - Single Run")
        print(f"📝 Clean log: {self.clean_logger.get_log_file_path()}")
        print("="*50)
        
        # Process tasks once
        self.process_tasks()
        
        # Print final stats
        self._print_stats()
        print("\n✅ Run complete")
    
    def start(self, interval_seconds: int = 5):
        """
        Start the Cron Agent with continuous loop
        
        Used for manual/testing runs only.
        For production, use OS scheduler with run_once().
        
        Args:
            interval_seconds: Interval between runs (in seconds)
        """
        print("🚀 Cron Agent - Continuous Mode (Testing)")
        print(f"⏰ Will run every {interval_seconds} seconds")
        print(f"📝 Clean log (prompts and responses only): {self.clean_logger.get_log_file_path()}")
        print("🛑 Press Ctrl+C to stop")
        print()
        print("ℹ️  Note: This mode is for testing only.")
        print("   For production, use OS scheduler: ./cronagent install")
        print("="*50)
        
        # Initial run immediately
        self.process_tasks()
        
        # Schedule subsequent runs
        schedule.every(interval_seconds).seconds.do(self.process_tasks)
        
        # Infinite loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Cron Agent stopped")
            self._print_stats()
            print("\n👋 Goodbye!")


def main():
    """
    Main entry point
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Cron Agent - Smart Task Automation"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install OS-specific scheduler (LaunchAgent/systemd/cron/Task Scheduler)"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Uninstall scheduler"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show scheduler status"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Interval in seconds (default: from REFRESH_INTERVAL_SECONDS in .env)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (used by OS scheduler)"
    )
    
    args = parser.parse_args()
    
    # Handle scheduler management commands
    if args.install or args.uninstall or args.status:
        from scheduler.factory import create_scheduler
        from dotenv import load_dotenv
        
        # Load .env file to get default interval
        project_root = Path(__file__).parent.parent
        load_dotenv(project_root / ".env")
        
        # Get interval from args or env variable (in seconds)
        interval_seconds = args.interval
        if interval_seconds is None:
            interval_seconds = int(os.getenv('REFRESH_INTERVAL_SECONDS', 300))
        
        # For display purposes
        interval_minutes = interval_seconds // 60
        
        script_path = Path(__file__).resolve()
        
        try:
            scheduler = create_scheduler(script_path, interval_seconds=interval_seconds)
            
            if args.install:
                # Validate Todoist token before installing
                print("🔍 Validating configuration...")
                
                todoist_token = os.getenv('TODOIST_TOKEN')
                
                if not todoist_token:
                    print("❌ Error: TODOIST_TOKEN not configured!")
                    print("\nPlease run setup first:")
                    print("  ./cronagent setup")
                    return
                
                # Validate token
                todoist_api = TodoistAPI(todoist_token)
                if not todoist_api.validate_token():
                    print("\n❌ Failed to validate Todoist API token!")
                    print("\nPlease fix the token and run setup again:")
                    print("  ./cronagent setup")
                    return
                
                print("✅ Configuration validated successfully!")
                print()
                
                print("📦 Installing scheduler...")
                print(f"   Type: {scheduler.__class__.__name__}")
                
                # Display interval correctly
                if interval_seconds < 60:
                    print(f"   Interval: {interval_seconds} seconds")
                elif interval_seconds % 60 == 0:
                    print(f"   Interval: {interval_minutes} minutes")
                else:
                    print(f"   Interval: {interval_seconds} seconds ({interval_minutes}m {interval_seconds % 60}s)")
                print()
                
                if scheduler.install():
                    print()
                    if scheduler.start():
                        print()
                        print("✅ Scheduler installed and started successfully!")
                        print()
                        print("Next steps:")
                        print("  1. Check status: ./cronagent status")
                        print("  2. View logs in logs/ and clean_logs/ directories")
                        print("  3. Monitor task execution in Todoist")
                    else:
                        print("❌ Failed to start scheduler")
                else:
                    print("❌ Installation failed")
            
            elif args.uninstall:
                print("🗑️  Uninstalling scheduler...")
                if scheduler.uninstall():
                    print("✅ Scheduler uninstalled successfully!")
                else:
                    print("❌ Uninstall failed")
            
            elif args.status:
                print("📊 Scheduler Status")
                print("=" * 50)
                status = scheduler.status()
                
                print(f"Type: {scheduler.__class__.__name__}")
                print(f"Installed: {'✅ Yes' if status['installed'] else '❌ No'}")
                
                if 'running' in status:
                    print(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
                
                if status.get('plist_path'):
                    print(f"Config: {status['plist_path']}")
                elif status.get('service_path'):
                    print(f"Service: {status['service_path']}")
                    print(f"Timer: {status.get('timer_path')}")
                elif status.get('task_name'):
                    print(f"Task: {status['task_name']}")
                
                if status.get('output'):
                    print("\nDetails:")
                    print("-" * 50)
                    print(status['output'])
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        return
    
    # Regular execution (no scheduler management)
    # Change to project root directory (where .env is)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Load Token from environment variable
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")  # Load from .env file in root
    
    todoist_token = os.getenv('TODOIST_TOKEN')
    
    if not todoist_token:
        print("❌ Error: TODOIST_TOKEN not configured!")
        print("\nInstructions:")
        print("1. Get Token from: https://todoist.com/app/settings/integrations/developer")
        print("2. Edit .env file and add:")
        print("   TODOIST_TOKEN=your-token-here")
        print("3. Run the script again")
        return
    
    # Validate Todoist API token before starting
    print("🔍 Validating Todoist API connection...")
    todoist_api = TodoistAPI(todoist_token)
    
    if not todoist_api.validate_token():
        print("\n❌ Failed to validate Todoist API token!")
        print("\nPossible issues:")
        print("1. Token is invalid or expired")
        print("2. Internet connection issue")
        print("3. Todoist API is down or endpoint has changed")
        print("\nHow to fix:")
        print("1. Get a new token from: https://todoist.com/app/settings/integrations/developer")
        print("2. Update your .env file with the new token")
        print("3. Make sure you have internet connection")
        print("4. Try running: ./cronagent setup")
        return
    
    print("✅ Todoist API connection validated successfully!")
    print()
    
    # Use configuration from environment
    clean_log_dir = 'clean_logs'
    
    # Get interval from environment variable (in seconds)
    interval_seconds = int(os.getenv('REFRESH_INTERVAL_SECONDS', 300))
    
    # Get code location from environment
    code_location = os.getenv('CODE_LOCATION', CursorAgent.DEFAULT_CODE_LOCATION)
    
    print("🤖 Cursor CLI mode: ENABLED (required)")
    print("   Tasks will be executed by real Cursor AI")
    print(f"   Code location: {code_location}")
    print()
    
    # Create the agent
    agent = CronAgent(
        todoist_token,
        clean_log_dir=clean_log_dir,
        code_location=code_location,
    )
    
    # Run mode: once (OS scheduler) or continuous (manual)
    if args.once:
        # Single run for OS scheduler
        agent.run_once()
    else:
        # Continuous loop for manual testing
        agent.start(interval_seconds=interval_seconds)


if __name__ == "__main__":
    main()

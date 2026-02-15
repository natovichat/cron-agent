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
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
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
            tasks = response.json()
            
            # Filter incomplete tasks
            active_tasks = [t for t in tasks if not t.get('is_completed', False)]
            
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
    Simulation of Cursor AI Agent
    (In production this will be real Cursor integration)
    """
    
    def __init__(self, clean_logger: CleanLogger = None):
        self.execution_log = []
        self.clean_logger = clean_logger
    
    def execute(self, task_content: str, task_id: str = None) -> Dict[str, any]:
        """
        Execute task using AI
        
        Args:
            task_content: Task description
            task_id: Task ID (for logging)
            
        Returns:
            Execution result
        """
        print(f"🤖 Cursor AI processing: {task_content}")
        
        # Here will be the real Cursor AI code
        # For now, we return a simulation
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Identify task type (simple example)
        action_taken = self._analyze_and_execute(task_content)
        
        result = {
            "success": True,
            "task": task_content,
            "timestamp": timestamp,
            "action_taken": action_taken,
            "duration": "0.5s"
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
    
    def _analyze_and_execute(self, content: str) -> str:
        """
        Analyze and execute the task
        
        Args:
            content: Task content
            
        Returns:
            Description of action taken
        """
        content_lower = content.lower()
        
        # Examples of task type detection
        if "email" in content_lower:
            return "✉️ Automated email sent to client"
        
        elif "report" in content_lower:
            return "📊 Detailed report created and emailed"
        
        elif "backup" in content_lower:
            return "💾 Backup of all important files completed"
        
        elif "update" in content_lower:
            return "🔄 Database updated successfully"
        
        else:
            return f"✅ Task '{content}' completed successfully"


class CronAgent:
    """
    Main engine of the system - schedules and executes tasks
    """
    
    def __init__(self, todoist_token: str, clean_log_dir: str = "clean_logs"):
        """
        Initialize the Cron Agent
        
        Args:
            todoist_token: Todoist API Token
            clean_log_dir: Directory for clean log
        """
        self.todoist = TodoistAPI(todoist_token)
        self.clean_logger = CleanLogger(clean_log_dir)
        self.cursor = CursorAgent(clean_logger=self.clean_logger)
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
            
            # Update in Todoist
            comment = f"""
🎯 Execution Result:
- Status: {"✅ Success" if result['success'] else "❌ Failed"}
- Action: {result['action_taken']}
- Time: {result['timestamp']}
- Duration: {result['duration']}
"""
            
            self.todoist.add_comment(task_id, comment)
            self.todoist.complete_task(task_id)
            
            # Update statistics
            self.stats['total_processed'] += 1
            if result['success']:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
            
            print(f"✅ Task completed successfully")
            
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
    
    def start(self, interval_seconds: int = 5):
        """
        Start the Cron Agent
        
        Args:
            interval_seconds: Interval between runs (in seconds)
        """
        print("🚀 Cron Agent starting!")
        print(f"⏰ Will run every {interval_seconds} seconds")
        print(f"📝 Clean log (prompts and responses only): {self.clean_logger.get_log_file_path()}")
        print("🛑 Press Ctrl+C to stop")
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
        default=5,
        help="Interval in minutes (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Handle scheduler management commands
    if args.install or args.uninstall or args.status:
        from scheduler.factory import create_scheduler
        
        script_path = Path(__file__).resolve()
        
        try:
            scheduler = create_scheduler(script_path, interval_minutes=args.interval)
            
            if args.install:
                print("📦 Installing scheduler...")
                print(f"   Type: {scheduler.__class__.__name__}")
                print(f"   Interval: {args.interval} minutes")
                print()
                
                if scheduler.install():
                    print()
                    if scheduler.start():
                        print()
                        print("✅ Scheduler installed and started successfully!")
                        print()
                        print("Next steps:")
                        print("  1. Make sure TODOIST_TOKEN is set in .env file")
                        print(f"  2. Check status: python {Path(__file__).name} --status")
                        print("  3. View logs in logs/ and clean_logs/ directories")
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
    
    # Use default configuration
    clean_log_dir = 'clean_logs'
    interval_seconds = 5  # For manual runs, keep 5 seconds for demo
    
    # Create and start the agent
    agent = CronAgent(todoist_token, clean_log_dir=clean_log_dir)
    agent.start(interval_seconds=interval_seconds)


if __name__ == "__main__":
    main()

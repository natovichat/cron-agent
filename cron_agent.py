#!/usr/bin/env python3
"""
Cron Agent - אוטומציה חכמה לניהול משימות
=========================================

מערכת שמתזמנת פעולות חוזרות, קוראת משימות מ-Todoist,
שולחת אותן ל-Cursor AI לביצוע, ומעדכנת את התוצאות בחזרה.

Author: Your Name
Date: 2025-02-15
"""

import os
import time
import schedule
import requests
from datetime import datetime
from typing import List, Dict, Optional
import json
from pathlib import Path


class CleanLogger:
    """
    לוג נקי שמראה רק פרומפטים ותשובות, ללא דיבאג
    """
    
    def __init__(self, log_dir: str = "clean_logs"):
        """
        אתחול ה-logger
        
        Args:
            log_dir: תיקייה לשמירת הלוגים
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # יצירת שם קובץ עם תאריך
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"conversation_{today}.log"
    
    def log_conversation(self, prompt: str, response: str, task_id: str = None):
        """
        רישום שיחה בלוג הנקי
        
        Args:
            prompt: הפרומפט ששלחנו
            response: התשובה שקיבלנו
            task_id: מזהה המשימה (אופציונלי)
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
        
        # כתיבה לקובץ
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def get_log_file_path(self) -> str:
        """
        קבלת נתיב הקובץ
        
        Returns:
            נתיב הקובץ
        """
        return str(self.log_file)


class TodoistAPI:
    """
    ממשק לעבודה עם Todoist API
    """
    
    def __init__(self, token: str):
        """
        אתחול ה-API
        
        Args:
            token: API Token מ-Todoist
        """
        self.token = token
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_tasks(self) -> List[Dict]:
        """
        קבלת כל המשימות הפעילות
        
        Returns:
            רשימת משימות
        """
        try:
            response = requests.get(
                f"{self.base_url}/tasks",
                headers=self.headers
            )
            response.raise_for_status()
            tasks = response.json()
            
            # סינון משימות שלא הושלמו
            active_tasks = [t for t in tasks if not t.get('is_completed', False)]
            
            print(f"📋 נמצאו {len(active_tasks)} משימות פעילות")
            return active_tasks
            
        except Exception as e:
            print(f"❌ שגיאה בקריאת משימות: {e}")
            return []
    
    def complete_task(self, task_id: str) -> bool:
        """
        סימון משימה כהושלמה
        
        Args:
            task_id: מזהה המשימה
            
        Returns:
            האם הפעולה הצליחה
        """
        try:
            response = requests.post(
                f"{self.base_url}/tasks/{task_id}/close",
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ שגיאה בסגירת משימה {task_id}: {e}")
            return False
    
    def add_comment(self, task_id: str, comment: str) -> bool:
        """
        הוספת הערה למשימה
        
        Args:
            task_id: מזהה המשימה
            comment: תוכן ההערה
            
        Returns:
            האם הפעולה הצליחה
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
            print(f"❌ שגיאה בהוספת הערה: {e}")
            return False


class CursorAgent:
    """
    סימולציה של Cursor AI Agent
    (בפועל זה יהיה אינטגרציה אמיתית עם Cursor)
    """
    
    def __init__(self, clean_logger: CleanLogger = None):
        self.execution_log = []
        self.clean_logger = clean_logger
    
    def execute(self, task_content: str, task_id: str = None) -> Dict[str, any]:
        """
        ביצוע משימה באמצעות AI
        
        Args:
            task_content: תיאור המשימה
            task_id: מזהה המשימה (לצורך לוגינג)
            
        Returns:
            תוצאת הביצוע
        """
        print(f"🤖 Cursor AI מעבד: {task_content}")
        
        # כאן יהיה הקוד האמיתי של Cursor AI
        # לצורך דוגמה, נחזיר סימולציה
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # זיהוי סוג המשימה (דוגמה פשוטה)
        action_taken = self._analyze_and_execute(task_content)
        
        result = {
            "success": True,
            "task": task_content,
            "timestamp": timestamp,
            "action_taken": action_taken,
            "duration": "0.5s"
        }
        
        # כתיבה ללוג הנקי (רק פרומפט ותשובה)
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
        ניתוח וביצוע המשימה
        
        Args:
            content: תוכן המשימה
            
        Returns:
            תיאור הפעולה שבוצעה
        """
        content_lower = content.lower()
        
        # דוגמאות לזיהוי סוגי משימות
        if "מייל" in content_lower or "email" in content_lower:
            return "✉️ נשלח מייל אוטומטי ללקוח"
        
        elif "דוח" in content_lower or "report" in content_lower:
            return "📊 נוצר דוח מפורט ונשלח למייל"
        
        elif "גיבוי" in content_lower or "backup" in content_lower:
            return "💾 בוצע גיבוי של כל הקבצים החשובים"
        
        elif "עדכון" in content_lower or "update" in content_lower:
            return "🔄 מסד הנתונים עודכן בהצלחה"
        
        else:
            return f"✅ המשימה '{content}' בוצעה בהצלחה"


class CronAgent:
    """
    המנוע הראשי של המערכת - מתזמן ומפעיל משימות
    """
    
    def __init__(self, todoist_token: str, clean_log_dir: str = "clean_logs"):
        """
        אתחול ה-Cron Agent
        
        Args:
            todoist_token: API Token של Todoist
            clean_log_dir: תיקייה ללוג הנקי
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
        
        # הדפסת מיקום הלוג הנקי
        print(f"📝 לוג נקי נשמר ב: {self.clean_logger.get_log_file_path()}")
    
    def process_tasks(self):
        """
        עיבוד כל המשימות הפעילות
        """
        print("\n" + "="*50)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # קבלת משימות
        tasks = self.todoist.get_tasks()
        
        if not tasks:
            print("💤 אין משימות חדשות לעיבוד")
            return
        
        # עיבוד כל משימה
        for task in tasks:
            self._process_single_task(task)
        
        # הצגת סטטיסטיקות
        self._print_stats()
    
    def _process_single_task(self, task: Dict):
        """
        עיבוד משימה בודדת
        
        Args:
            task: אובייקט המשימה
        """
        task_id = task['id']
        task_content = task['content']
        
        print(f"\n📝 מעבד משימה: {task_content}")
        
        try:
            # ביצוע המשימה ב-Cursor
            result = self.cursor.execute(task_content, task_id=task_id)
            
            # עדכון ב-Todoist
            comment = f"""
🎯 תוצאת ביצוע:
- סטטוס: {"✅ הצליח" if result['success'] else "❌ נכשל"}
- פעולה: {result['action_taken']}
- זמן: {result['timestamp']}
- משך: {result['duration']}
"""
            
            self.todoist.add_comment(task_id, comment)
            self.todoist.complete_task(task_id)
            
            # עדכון סטטיסטיקות
            self.stats['total_processed'] += 1
            if result['success']:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
            
            print(f"✅ המשימה הושלמה בהצלחה")
            
        except Exception as e:
            print(f"❌ שגיאה בעיבוד משימה: {e}")
            self.stats['failed'] += 1
    
    def _print_stats(self):
        """
        הצגת סטטיסטיקות
        """
        uptime = datetime.now() - self.stats['start_time']
        
        print("\n" + "-"*50)
        print("📊 סטטיסטיקות:")
        print(f"   🎯 סה\"כ משימות: {self.stats['total_processed']}")
        print(f"   ✅ הצליחו: {self.stats['successful']}")
        print(f"   ❌ נכשלו: {self.stats['failed']}")
        print(f"   ⏱️  זמן פעילות: {str(uptime).split('.')[0]}")
        print("-"*50)
    
    def start(self, interval_seconds: int = 5):
        """
        הפעלת ה-Cron Agent
        
        Args:
            interval_seconds: מרווח זמן בין הרצות (בשניות)
        """
        print("🚀 Cron Agent מתחיל לפעול!")
        print(f"⏰ ירוץ כל {interval_seconds} שניות")
        print(f"📝 לוג נקי (פרומפטים ותשובות בלבד): {self.clean_logger.get_log_file_path()}")
        print("🛑 לחץ Ctrl+C לעצירה")
        print("="*50)
        
        # הרצה ראשונית מיידית
        self.process_tasks()
        
        # תזמון ההרצות הבאות
        schedule.every(interval_seconds).seconds.do(self.process_tasks)
        
        # לולאה אינסופית
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Cron Agent נעצר")
            self._print_stats()
            print("\n👋 להתראות!")


def main():
    """
    נקודת הכניסה הראשית
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Cron Agent - אוטומציה חכמה לניהול משימות"
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
        from pathlib import Path
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
    # קריאת Token מ-environment variable
    from dotenv import load_dotenv
    load_dotenv()  # Load from .env file
    
    todoist_token = os.getenv('TODOIST_TOKEN')
    
    if not todoist_token:
        print("❌ שגיאה: TODOIST_TOKEN לא הוגדר!")
        print("\nהוראות:")
        print("1. קבל Token מ: https://todoist.com/app/settings/integrations/developer")
        print("2. ערוך את קובץ .env והוסף:")
        print("   TODOIST_TOKEN=your-token-here")
        print("3. הרץ את הסקריפט שוב")
        return
    
    # יצירה והפעלה של ה-agent
    agent = CronAgent(todoist_token)
    agent.start(interval_seconds=5)  # כל 5 שניות


if __name__ == "__main__":
    main()

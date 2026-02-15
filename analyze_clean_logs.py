#!/usr/bin/env python3
"""
ניתוח לוגים נקיים - Clean Logs Analyzer
=========================================

סקריפט לניתוח הלוגים הנקיים והצגת סטטיסטיקות מעניינות.

Usage:
    python analyze_clean_logs.py
"""

import os
import re
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import Dict, List, Tuple


class CleanLogsAnalyzer:
    """
    מנתח לוגים נקיים
    """
    
    def __init__(self, log_dir: str = "clean_logs"):
        self.log_dir = Path(log_dir)
        self.conversations = []
    
    def load_logs(self):
        """
        טעינת כל קבצי הלוג
        """
        if not self.log_dir.exists():
            print(f"❌ תיקייה לא קיימת: {self.log_dir}")
            return
        
        log_files = sorted(self.log_dir.glob("conversation_*.log"))
        
        if not log_files:
            print("⚠️  לא נמצאו קבצי לוג")
            return
        
        print(f"📂 קורא {len(log_files)} קבצי לוג...")
        
        for log_file in log_files:
            self._parse_log_file(log_file)
        
        print(f"✅ נטענו {len(self.conversations)} שיחות\n")
    
    def _parse_log_file(self, log_file: Path):
        """
        פענוח קובץ לוג בודד
        """
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # חיפוש כל השיחות
        pattern = r'\[([^\]]+)\](?:\s+Task ID: ([^\n]+))?\s+📤 PROMPT:\s+([^\n]+(?:\n(?!📥)[^\n]+)*)\s+📥 RESPONSE:\s+([^\n]+(?:\n(?!=====)[^\n]+)*)'
        
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            timestamp_str, task_id, prompt, response = match.groups()
            
            try:
                timestamp = datetime.strptime(timestamp_str.strip(), "%Y-%m-%d %H:%M:%S")
            except:
                timestamp = None
            
            self.conversations.append({
                'timestamp': timestamp,
                'task_id': task_id.strip() if task_id else None,
                'prompt': prompt.strip(),
                'response': response.strip()
            })
    
    def analyze(self):
        """
        ניתוח הלוגים
        """
        if not self.conversations:
            print("❌ אין שיחות לניתוח")
            return
        
        print("="*70)
        print("📊 ניתוח לוגים נקיים")
        print("="*70)
        print()
        
        self._general_stats()
        self._temporal_analysis()
        self._response_types_analysis()
        self._prompt_analysis()
    
    def _general_stats(self):
        """
        סטטיסטיקות כלליות
        """
        print("📈 סטטיסטיקות כלליות:")
        print("-" * 70)
        print(f"   סה\"כ שיחות: {len(self.conversations)}")
        
        # תאריכים
        timestamps = [c['timestamp'] for c in self.conversations if c['timestamp']]
        if timestamps:
            first_date = min(timestamps).strftime("%Y-%m-%d")
            last_date = max(timestamps).strftime("%Y-%m-%d")
            print(f"   תקופה: {first_date} - {last_date}")
        
        # אורכי פרומפטים
        prompt_lengths = [len(c['prompt']) for c in self.conversations]
        avg_prompt_length = sum(prompt_lengths) / len(prompt_lengths)
        print(f"   אורך פרומפט ממוצע: {avg_prompt_length:.0f} תווים")
        
        # אורכי תשובות
        response_lengths = [len(c['response']) for c in self.conversations]
        avg_response_length = sum(response_lengths) / len(response_lengths)
        print(f"   אורך תשובה ממוצע: {avg_response_length:.0f} תווים")
        print()
    
    def _temporal_analysis(self):
        """
        ניתוח זמני
        """
        print("⏰ ניתוח זמני:")
        print("-" * 70)
        
        timestamps = [c['timestamp'] for c in self.conversations if c['timestamp']]
        if not timestamps:
            print("   אין נתוני זמן זמינים\n")
            return
        
        # שיחות לפי תאריך
        dates = [t.date() for t in timestamps]
        date_counter = Counter(dates)
        
        print("   שיחות לפי יום:")
        for date, count in sorted(date_counter.items()):
            print(f"      {date}: {'█' * count} {count}")
        
        # שיחות לפי שעה
        hours = [t.hour for t in timestamps]
        hour_counter = Counter(hours)
        
        print("\n   שיחות לפי שעה:")
        for hour in range(24):
            count = hour_counter.get(hour, 0)
            if count > 0:
                bar = '█' * (count // 2 if count > 10 else count)
                print(f"      {hour:02d}:00 - {hour:02d}:59: {bar} {count}")
        print()
    
    def _response_types_analysis(self):
        """
        ניתוח סוגי תשובות
        """
        print("🎯 סוגי תשובות:")
        print("-" * 70)
        
        # חיפוש אמוג'י בתשובות
        emojis = []
        for conv in self.conversations:
            response = conv['response']
            # חיפוש אמוג'י נפוצים
            if '✉️' in response or 'מייל' in response.lower():
                emojis.append('✉️ Email')
            elif '📊' in response or 'דוח' in response.lower():
                emojis.append('📊 Report')
            elif '💾' in response or 'גיבוי' in response.lower():
                emojis.append('💾 Backup')
            elif '🔄' in response or 'עדכון' in response.lower():
                emojis.append('🔄 Update')
            elif '✅' in response:
                emojis.append('✅ Success')
            else:
                emojis.append('❓ Other')
        
        emoji_counter = Counter(emojis)
        
        for emoji_type, count in emoji_counter.most_common():
            percentage = (count / len(self.conversations)) * 100
            bar = '█' * int(percentage / 5)
            print(f"   {emoji_type:15} {bar} {count} ({percentage:.1f}%)")
        print()
    
    def _prompt_analysis(self):
        """
        ניתוח פרומפטים
        """
        print("💬 ניתוח פרומפטים:")
        print("-" * 70)
        
        # מילות מפתח נפוצות
        all_prompts = ' '.join([c['prompt'].lower() for c in self.conversations])
        
        # ספירת מילים נפוצות (עברית ואנגלית)
        keywords = ['מייל', 'email', 'דוח', 'report', 'עדכן', 'update', 
                   'גיבוי', 'backup', 'שלח', 'send', 'צור', 'create',
                   'בדוק', 'check', 'נתח', 'analyze']
        
        keyword_counts = {}
        for keyword in keywords:
            count = all_prompts.count(keyword)
            if count > 0:
                keyword_counts[keyword] = count
        
        if keyword_counts:
            print("   מילות מפתח נפוצות:")
            for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"      {keyword:15} {count} פעמים")
        
        print()
        
        # הפרומפטים הארוכים ביותר
        print("   הפרומפטים הארוכים ביותר:")
        sorted_by_length = sorted(self.conversations, key=lambda x: len(x['prompt']), reverse=True)
        for i, conv in enumerate(sorted_by_length[:3], 1):
            prompt_preview = conv['prompt'][:60] + "..." if len(conv['prompt']) > 60 else conv['prompt']
            print(f"      {i}. ({len(conv['prompt'])} תווים) {prompt_preview}")
        print()
    
    def export_summary(self, output_file: str = "logs_summary.txt"):
        """
        ייצוא סיכום לקובץ
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("📊 סיכום ניתוח לוגים נקיים\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"נוצר: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"סה\"כ שיחות: {len(self.conversations)}\n\n")
            
            f.write("שיחות אחרונות:\n")
            f.write("-"*70 + "\n")
            for conv in self.conversations[-10:]:
                f.write(f"\n[{conv['timestamp']}]\n")
                f.write(f"Prompt: {conv['prompt'][:100]}...\n")
                f.write(f"Response: {conv['response'][:100]}...\n")
        
        print(f"✅ סיכום יוצא ל: {output_file}")


def main():
    """
    נקודת כניסה ראשית
    """
    analyzer = CleanLogsAnalyzer()
    analyzer.load_logs()
    
    if analyzer.conversations:
        analyzer.analyze()
        
        # שאלה אם לייצא
        try:
            export = input("\nלייצא סיכום לקובץ? (y/n): ").lower()
            if export == 'y':
                analyzer.export_summary()
        except KeyboardInterrupt:
            print("\n\n👋 ביי!")


if __name__ == "__main__":
    main()

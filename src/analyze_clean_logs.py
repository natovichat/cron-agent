#!/usr/bin/env python3
"""
Clean Logs Analyzer
===================

Script to analyze clean logs and show interesting statistics.

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
    Analyzer for clean logs
    """
    
    def __init__(self, log_dir: str = "clean_logs"):
        self.log_dir = Path(log_dir)
        self.conversations = []
    
    def load_logs(self):
        """
        Load all log files
        """
        if not self.log_dir.exists():
            print(f"❌ Directory does not exist: {self.log_dir}")
            return
        
        log_files = sorted(self.log_dir.glob("conversation_*.log"))
        
        if not log_files:
            print("⚠️  No log files found")
            return
        
        print(f"📂 Reading {len(log_files)} log files...")
        
        for log_file in log_files:
            self._parse_log_file(log_file)
        
        print(f"✅ Loaded {len(self.conversations)} conversations\n")
    
    def _parse_log_file(self, log_file: Path):
        """
        Parse a single log file
        """
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Search for all conversations
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
        Analyze the logs
        """
        if not self.conversations:
            print("❌ No conversations to analyze")
            return
        
        print("="*70)
        print("📊 Clean Logs Analysis")
        print("="*70)
        print()
        
        self._general_stats()
        self._temporal_analysis()
        self._response_types_analysis()
        self._prompt_analysis()
    
    def _general_stats(self):
        """
        General statistics
        """
        print("📈 General Statistics:")
        print("-" * 70)
        print(f"   Total conversations: {len(self.conversations)}")
        
        # Dates
        timestamps = [c['timestamp'] for c in self.conversations if c['timestamp']]
        if timestamps:
            first_date = min(timestamps).strftime("%Y-%m-%d")
            last_date = max(timestamps).strftime("%Y-%m-%d")
            print(f"   Period: {first_date} - {last_date}")
        
        # Prompt lengths
        prompt_lengths = [len(c['prompt']) for c in self.conversations]
        avg_prompt_length = sum(prompt_lengths) / len(prompt_lengths)
        print(f"   Average prompt length: {avg_prompt_length:.0f} characters")
        
        # Response lengths
        response_lengths = [len(c['response']) for c in self.conversations]
        avg_response_length = sum(response_lengths) / len(response_lengths)
        print(f"   Average response length: {avg_response_length:.0f} characters")
        print()
    
    def _temporal_analysis(self):
        """
        Temporal analysis
        """
        print("⏰ Temporal Analysis:")
        print("-" * 70)
        
        timestamps = [c['timestamp'] for c in self.conversations if c['timestamp']]
        if not timestamps:
            print("   No timestamp data available\n")
            return
        
        # Conversations by date
        dates = [t.date() for t in timestamps]
        date_counter = Counter(dates)
        
        print("   Conversations by day:")
        for date, count in sorted(date_counter.items()):
            print(f"      {date}: {'█' * count} {count}")
        
        # Conversations by hour
        hours = [t.hour for t in timestamps]
        hour_counter = Counter(hours)
        
        print("\n   Conversations by hour:")
        for hour in range(24):
            count = hour_counter.get(hour, 0)
            if count > 0:
                bar = '█' * (count // 2 if count > 10 else count)
                print(f"      {hour:02d}:00 - {hour:02d}:59: {bar} {count}")
        print()
    
    def _response_types_analysis(self):
        """
        Response types analysis
        """
        print("🎯 Response Types:")
        print("-" * 70)
        
        # Search for emojis in responses
        emojis = []
        for conv in self.conversations:
            response = conv['response']
            # Search for common emojis
            if '✉️' in response or 'email' in response.lower():
                emojis.append('✉️ Email')
            elif '📊' in response or 'report' in response.lower():
                emojis.append('📊 Report')
            elif '💾' in response or 'backup' in response.lower():
                emojis.append('💾 Backup')
            elif '🔄' in response or 'update' in response.lower():
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
        Prompt analysis
        """
        print("💬 Prompt Analysis:")
        print("-" * 70)
        
        # Common keywords
        all_prompts = ' '.join([c['prompt'].lower() for c in self.conversations])
        
        # Count common words (English)
        keywords = ['email', 'report', 'update', 'backup', 'send', 'create',
                   'check', 'analyze', 'generate', 'build', 'test', 'fix']
        
        keyword_counts = {}
        for keyword in keywords:
            count = all_prompts.count(keyword)
            if count > 0:
                keyword_counts[keyword] = count
        
        if keyword_counts:
            print("   Common keywords:")
            for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"      {keyword:15} {count} times")
        
        print()
        
        # Longest prompts
        print("   Longest prompts:")
        sorted_by_length = sorted(self.conversations, key=lambda x: len(x['prompt']), reverse=True)
        for i, conv in enumerate(sorted_by_length[:3], 1):
            prompt_preview = conv['prompt'][:60] + "..." if len(conv['prompt']) > 60 else conv['prompt']
            print(f"      {i}. ({len(conv['prompt'])} chars) {prompt_preview}")
        print()
    
    def export_summary(self, output_file: str = "logs_summary.txt"):
        """
        Export summary to file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("📊 Clean Logs Analysis Summary\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total conversations: {len(self.conversations)}\n\n")
            
            f.write("Recent conversations:\n")
            f.write("-"*70 + "\n")
            for conv in self.conversations[-10:]:
                f.write(f"\n[{conv['timestamp']}]\n")
                f.write(f"Prompt: {conv['prompt'][:100]}...\n")
                f.write(f"Response: {conv['response'][:100]}...\n")
        
        print(f"✅ Summary exported to: {output_file}")


def main():
    """
    Main entry point
    """
    analyzer = CleanLogsAnalyzer()
    analyzer.load_logs()
    
    if analyzer.conversations:
        analyzer.analyze()
        
        # Ask if they want to export
        try:
            export = input("\nExport summary to file? (y/n): ").lower()
            if export == 'y':
                analyzer.export_summary()
        except KeyboardInterrupt:
            print("\n\n👋 Bye!")


if __name__ == "__main__":
    main()

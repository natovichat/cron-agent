"""
Scheduler abstraction layer for cross-platform task scheduling.

This package provides a unified interface for scheduling tasks across
different operating systems:
- macOS: LaunchAgents
- Linux: systemd timers or cron
- Windows: Task Scheduler
"""

from .factory import create_scheduler
from .base import BaseScheduler

__all__ = ['create_scheduler', 'BaseScheduler']

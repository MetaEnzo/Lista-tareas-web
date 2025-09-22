"""
Data models for the task list application.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """Represents a single task in the application."""
    text: str
    date_str: Optional[str] = None
    status: bool = False  # False = pending, True = completed
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            'text': self.text,
            'date_str': self.date_str,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary."""
        return cls(
            text=data['text'],
            date_str=data.get('date_str'),
            status=data.get('status', False)
        )

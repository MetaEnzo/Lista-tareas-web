"""
Storage module for handling task persistence with JSON.
"""

import json
import os
from typing import List
from models import Task


def load_tasks(filename: str = "tareas.json") -> List[Task]:
    """
    Load tasks from JSON file with robust error handling.
    
    Args:
        filename: Path to the JSON file
        
    Returns:
        List of Task objects
    """
    # If file doesn't exist, start with empty list
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Validate that data is a list
        if not isinstance(data, list):
            print(f"Warning: {filename} contains invalid data format. Starting with empty task list.")
            return []
            
        # Convert each task data to Task object
        tasks = []
        for i, task_data in enumerate(data):
            try:
                task = Task.from_dict(task_data)
                tasks.append(task)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Warning: Skipping invalid task at index {i}: {e}")
                continue
                
        return tasks
        
    except json.JSONDecodeError as e:
        print(f"Warning: {filename} is corrupted (invalid JSON). Starting with empty task list.")
        print(f"JSON Error: {e}")
        return []
    except PermissionError:
        print(f"Error: Permission denied reading {filename}")
        return []
    except Exception as e:
        print(f"Unexpected error loading {filename}: {e}")
        return []


def save_tasks(tasks: List[Task], filename: str = "tareas.json") -> bool:
    """
    Save tasks to JSON file with robust error handling.
    
    Args:
        tasks: List of Task objects to save
        filename: Path to the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert tasks to dictionary format
        data = [task.to_dict() for task in tasks]
        
        # Write to file with UTF-8 encoding and proper formatting
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except PermissionError:
        print(f"Error: Permission denied writing to {filename}")
        return False
    except OSError as e:
        print(f"Error: Cannot write to {filename}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error saving to {filename}: {e}")
        return False

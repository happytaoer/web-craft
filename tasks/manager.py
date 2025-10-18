"""
Task Manager - Responsible for task creation, storage, querying and updating
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Iterator
from datetime import datetime, timedelta

from .models import SpiderTask, TaskStatus, TaskType


class TaskManager:
    """Task Manager"""
    
    def __init__(self, tasks_dir: str = "tasks"):
        """
        Initialize task manager
        
        Args:
            tasks_dir: Task storage directory
        """
        self.tasks_dir = Path(tasks_dir)
        self.tasks_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.pending_dir = self.tasks_dir / "pending"
        self.running_dir = self.tasks_dir / "running"
        self.completed_dir = self.tasks_dir / "completed"
        self.failed_dir = self.tasks_dir / "failed"
        
        for dir_path in [self.pending_dir, self.running_dir, self.completed_dir, self.failed_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def _get_task_file_path(self, task_id: str, status: TaskStatus) -> Path:
        """Get task file path"""
        status_dir_map = {
            TaskStatus.PENDING: self.pending_dir,
            TaskStatus.RUNNING: self.running_dir,
            TaskStatus.COMPLETED: self.completed_dir,
            TaskStatus.FAILED: self.failed_dir,
            TaskStatus.CANCELLED: self.failed_dir
        }
        
        status_dir = status_dir_map.get(status, self.pending_dir)
        return status_dir / f"{task_id}.json"
    
    def _find_task_file(self, task_id: str) -> Optional[Path]:
        """Find task file"""
        for status in TaskStatus:
            file_path = self._get_task_file_path(task_id, status)
            if file_path.exists():
                return file_path
        return None
    
    def create_task(self, task: SpiderTask) -> str:
        """
        Create task
        
        Args:
            task: Spider task object
            
        Returns:
            Task ID
        """
        file_path = self._get_task_file_path(task.task_id, task.status)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(task.to_json())
        
        return task.task_id
    
    def get_task(self, task_id: str) -> Optional[SpiderTask]:
        """
        Get task
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object, returns None if not exists
        """
        file_path = self._find_task_file(task_id)
        if not file_path or not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return SpiderTask.from_json(f.read())
        except Exception:
            return None
    
    def update_task(self, task: SpiderTask) -> bool:
        """
        Update task
        
        Args:
            task: Task object
            
        Returns:
            Whether update was successful
        """
        # Find original file
        old_file_path = self._find_task_file(task.task_id)
        new_file_path = self._get_task_file_path(task.task_id, task.status)
        
        try:
            # Write new file
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(task.to_json())
            
            # If file path changed, delete old file
            if old_file_path and old_file_path != new_file_path and old_file_path.exists():
                old_file_path.unlink()
            
            return True
        except Exception:
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete task
        
        Args:
            task_id: Task ID
            
        Returns:
            Whether deletion was successful
        """
        file_path = self._find_task_file(task_id)
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        return False
    
    def list_tasks(
        self, 
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        limit: Optional[int] = None
    ) -> List[SpiderTask]:
        """
        List tasks
        
        Args:
            status: Task status filter
            task_type: Task type filter
            limit: Limit return count
            
        Returns:
            Task list
        """
        tasks = []
        
        # Determine directories to search
        if status:
            search_dirs = [self._get_task_file_path("", status).parent]
        else:
            search_dirs = [self.pending_dir, self.running_dir, self.completed_dir, self.failed_dir]
        
        # Traverse directories to find task files
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            for file_path in search_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        task = SpiderTask.from_json(f.read())
                    
                    # Type filter
                    if task_type and task.task_type != task_type:
                        continue
                    
                    tasks.append(task)
                    
                    # Limit count
                    if limit and len(tasks) >= limit:
                        break
                        
                except Exception:
                    continue
        
        # Sort by creation time
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        if limit:
            tasks = tasks[:limit]
        
        return tasks
    
    def get_pending_tasks(self, limit: Optional[int] = None) -> List[SpiderTask]:
        """Get pending tasks"""
        return self.list_tasks(status=TaskStatus.PENDING, limit=limit)
    
    def get_running_tasks(self) -> List[SpiderTask]:
        """Get running tasks"""
        return self.list_tasks(status=TaskStatus.RUNNING)
    
    def cleanup_old_tasks(self, days: int = 7) -> int:
        """
        Clean up old tasks
        
        Args:
            days: Days to retain
            
        Returns:
            Number of cleaned tasks
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        # Only clean completed and failed tasks
        for search_dir in [self.completed_dir, self.failed_dir]:
            if not search_dir.exists():
                continue
                
            for file_path in search_dir.glob("*.json"):
                try:
                    # Check file modification time
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        cleaned_count += 1
                except Exception:
                    continue
        
        return cleaned_count
    
    def get_task_stats(self) -> Dict[str, int]:
        """Get task statistics"""
        stats = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "total": 0
        }
        
        for status in TaskStatus:
            if status == TaskStatus.CANCELLED:
                continue
            tasks = self.list_tasks(status=status)
            count = len(tasks)
            stats[status.value] = count
            stats["total"] += count
        
        return stats
    
    def iter_pending_tasks(self) -> Iterator[SpiderTask]:
        """Iterate pending tasks"""
        while True:
            pending_tasks = self.get_pending_tasks(limit=1)
            if not pending_tasks:
                break
            
            task = pending_tasks[0]
            
            # Mark task as running
            task.update_status(TaskStatus.RUNNING)
            if self.update_task(task):
                yield task
            else:
                break

"""
Spider task data models
"""
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"      # Pending
    RUNNING = "running"      # Running
    COMPLETED = "completed"  # Completed
    FAILED = "failed"        # Failed
    CANCELLED = "cancelled"  # Cancelled


class TaskType(str, Enum):
    """Task type enumeration"""
    SINGLE = "single"        # Single URL crawling


@dataclass
class SpiderTask:
    """Spider task data class"""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    created_at: str
    updated_at: str
    
    # Crawling configuration
    urls: List[str]
    spider_name: str = "default"
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30
    max_retries: int = 3
    delay: float = 1.0
    
    # Removed export configuration - now only output to console
    
    # Execution results
    progress: float = 0.0
    processed_urls: int = 0
    successful_count: int = 0
    failed_count: int = 0
    error_message: Optional[str] = None
    result_files: Optional[Dict[str, str]] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.headers is None:
            self.headers = {}
        if self.result_files is None:
            self.result_files = {}
    
    @classmethod
    def create_single_task(
        cls,
        url: str,
        spider_name: str = "default",
        method: str = "GET",
        timeout: int = 30,
        max_retries: int = 3,
        delay: float = 1.0
    ) -> 'SpiderTask':
        """Create single URL crawling task"""
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        return cls(
            task_id=task_id,
            task_type=TaskType.SINGLE,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            urls=[url],
            spider_name=spider_name,
            method=method,
            headers={},  # Use default empty dict, system config provides default headers
            timeout=timeout,
            max_retries=max_retries,
            delay=delay
        )
    
    def update_status(self, status: TaskStatus, error_message: Optional[str] = None):
        """Update task status"""
        self.status = status
        self.updated_at = datetime.now().isoformat()
        if error_message:
            self.error_message = error_message
    
    def update_progress(self, processed_urls: int, successful_count: int, failed_count: int):
        """Update task progress"""
        self.processed_urls = processed_urls
        self.successful_count = successful_count
        self.failed_count = failed_count
        
        if len(self.urls) > 0:
            self.progress = (processed_urls / len(self.urls)) * 100
        
        self.updated_at = datetime.now().isoformat()
    
    def set_completed(self, result_files: Dict[str, str], execution_time: float):
        """Set task completed"""
        self.status = TaskStatus.COMPLETED
        self.result_files = result_files
        self.execution_time = execution_time
        self.progress = 100.0
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpiderTask':
        """Create task from dictionary"""
        # Convert enum types
        if isinstance(data.get('task_type'), str):
            data['task_type'] = TaskType(data['task_type'])
        if isinstance(data.get('status'), str):
            data['status'] = TaskStatus(data['status'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SpiderTask':
        """Create task from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

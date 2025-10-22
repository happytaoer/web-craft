"""
Spider Service Class - Integrates API with Task System
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

from tasks.manager import TaskManager
from tasks.models import SpiderTask
from config import Config
from tasks.models import TaskStatus, TaskType
from spiders.core.spider_loader import SpiderLoader
from .models import (
    SpiderTaskRequest, SpiderResponse, 
    TaskInfo
)

class SpiderService:
    """Spider Service Class - Now only responsible for creating tasks, does not directly execute crawling"""
    
    def __init__(self) -> None:
        self.task_manager = TaskManager(Config.DEFAULT_TASKS_DIR)
        self.spider_loader = SpiderLoader()
    
    async def crawl_single(self, request: SpiderTaskRequest) -> SpiderResponse:
        """Create single URL crawling task"""
        try:
            # Create task
            task = SpiderTask.create_single_task(
                url=request.url,
                spider_name=request.spider_name,
                method=request.method.value,
                timeout=request.timeout,
                max_retries=request.max_retries,
                delay=request.delay
            )
            
            # Save task
            task_id = self.task_manager.create_task(task)
            
            # Return successful task creation response
            return SpiderResponse(
                url=request.url,
                status_code=202,  # Accepted
                success=True,
                content_length=0,
                encoding="utf-8",
                headers={},
                task_id=task_id,
                error_message=None
            )
            
        except Exception as e:
            return SpiderResponse(
                url=request.url,
                status_code=500,
                success=False,
                content_length=0,
                encoding="utf-8",
                headers={},
                error_message=f"Task creation failed: {str(e)}"
            )
    
    def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """Get task status"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return None
        
        # Convert to API model
        return TaskInfo(
            task_id=task.task_id,
            status=task.status,
            created_at=task.created_at,
            started_at=task.updated_at if task.status != TaskStatus.PENDING else None,
            completed_at=task.updated_at if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] else None,
            progress=task.progress,
            error_message=task.error_message
        )
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get task result"""
        task = self.task_manager.get_task(task_id)
        if not task or task.status != TaskStatus.COMPLETED:
            return None
        
        # Build single task result response
        return SpiderResponse(
            url=task.urls[0] if task.urls else "",
            status_code=200 if task.successful_count > 0 else 500,
            success=task.successful_count > 0,
            content_length=0,
            encoding="utf-8",
            headers={},
            task_id=task.task_id,
            error_message=task.error_message
        )
    
    def get_available_spiders(self) -> Dict[str, str]:
        """Get list of available spiders"""
        return self.spider_loader.list_spiders()
    
    def close(self) -> None:
        """Close service"""
        pass

"""
Spider Service Class - Integrates API with RQ Task Queue
"""
from typing import Dict, Optional, Any
from datetime import datetime

from tasks.queue import get_task_queue
from tasks.worker_tasks import execute_spider_task
from spiders.core.spider_loader import SpiderLoader
from .models import (
    SpiderTaskRequest, SpiderResponse, 
    TaskInfo
)

class SpiderService:
    """Spider Service Class - Uses RQ for task management"""
    
    def __init__(self) -> None:
        self.task_queue = get_task_queue()
        self.spider_loader = SpiderLoader()
    
    async def crawl_single(self, request: SpiderTaskRequest) -> SpiderResponse:
        """Create single URL crawling task and enqueue to RQ"""
        try:
            # Enqueue task to RQ
            job = self.task_queue.enqueue_task(
                execute_spider_task,
                url=request.url,
                spider_name=request.spider_name,
                method=request.method.value,
                timeout=request.timeout,
                max_retries=request.max_retries
            )
            
            # Return successful task creation response
            return SpiderResponse(
                url=request.url,
                status_code=202,  # Accepted
                success=True,
                content_length=0,
                encoding="utf-8",
                headers={},
                task_id=job.id,
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
        """Get task status from RQ job"""
        job = self.task_queue.get_job(task_id)
        if not job:
            return None
        
        # Map RQ job status to our TaskStatus
        status_map = {
            'queued': 'pending',
            'started': 'running',
            'finished': 'completed',
            'failed': 'failed',
            'deferred': 'pending',
            'scheduled': 'pending',
            'stopped': 'failed',
            'canceled': 'failed'
        }
        
        status = status_map.get(job.get_status(), 'pending')
        
        # Get error message if failed
        error_message = None
        if status == 'failed' and job.exc_info:
            error_message = str(job.exc_info)
        
        return TaskInfo(
            task_id=job.id,
            status=status,
            created_at=job.created_at.isoformat() if job.created_at else datetime.now().isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            completed_at=job.ended_at.isoformat() if job.ended_at else None,
            error_message=error_message
        )
    
    def get_available_spiders(self) -> Dict[str, str]:
        """Get list of available spiders"""
        return self.spider_loader.list_spiders()
    
    def close(self) -> None:
        """Close service"""
        pass

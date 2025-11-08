"""
Spider Service Class - Integrates API with RQ Task Queue
"""

from tasks.queue import get_task_queue
from tasks.worker_tasks import execute_spider_task
from spiders.core.spider_loader import SpiderLoader
from .models import (
    SpiderTaskRequest, SpiderResponse
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
                timeout=request.timeout
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
    
    def get_available_spiders(self) -> dict[str, str]:
        """Get list of available spiders"""
        return self.spider_loader.list_spiders()
    
    def close(self) -> None:
        """Close service"""
        pass

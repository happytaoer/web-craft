"""
Spider Service Class - Integrates API with RQ Task Queue
"""
from typing import Dict
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
    
    def crawl_single(self, request: SpiderTaskRequest) -> SpiderResponse:
        """Create single URL crawling task and enqueue to RQ"""
        try:
            # Get spider to retrieve its start_url for display
            spider = self.spider_loader.get_spider(request.spider_name)
            if not spider:
                raise ValueError(f"Spider '{request.spider_name}' not found")
            
            display_url = spider.start_url or f"<{request.spider_name} no URL configured>"
            
            # Enqueue task to RQ
            job = self.task_queue.enqueue_task(
                execute_spider_task,
                spider_name=request.spider_name,
                timeout=request.timeout
            )
            
            # Return successful task creation response
            return SpiderResponse(
                url=display_url,
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
                url=f"<{request.spider_name}>",
                status_code=500,
                success=False,
                content_length=0,
                encoding="utf-8",
                headers={},
                error_message=f"Task creation failed: {str(e)}"
            )
    
    def get_available_spiders(self) -> Dict[str, str]:
        """Get list of available spiders"""
        return self.spider_loader.list_spiders()
    
    def close(self) -> None:
        """Close service"""
        pass

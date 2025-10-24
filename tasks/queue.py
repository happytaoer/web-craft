"""
RQ Task Queue - Redis-based task queue management
"""
import redis
from rq import Queue
from typing import Optional
from config import config


class TaskQueue:
    """RQ Task Queue Manager"""
    
    def __init__(self):
        """Initialize task queue"""
        # Create Redis connection
        redis_config = config.redis
        
        # Build Redis connection parameters
        connection_params = {
            'host': redis_config.host,
            'port': redis_config.port,
            'db': redis_config.db,
        }
        
        # Add password if provided
        if redis_config.password:
            connection_params['password'] = redis_config.password
        
        self.redis_conn = redis.Redis(**connection_params)
        
        # Create RQ queue
        self.queue = Queue(redis_config.queue_name, connection=self.redis_conn)
    
    def enqueue_task(self, func, *args, **kwargs):
        """
        Enqueue a task with retry mechanism
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            RQ Job object
        """
        # Enqueue task with retry configuration
        # retry: Retry object that specifies max retries and intervals
        from rq import Retry
        
        job = self.queue.enqueue(
            func, 
            *args, 
            retry=Retry(max=config.spider.max_retries, interval=10),
            **kwargs
        )
        return job
    
    def get_job(self, job_id: str):
        """
        Get job by ID
        
        Args:
            job_id: Job ID
            
        Returns:
            RQ Job object or None
        """
        from rq.job import Job
        try:
            return Job.fetch(job_id, connection=self.redis_conn)
        except Exception:
            return None
    
    def get_queue_length(self) -> int:
        """Get queue length"""
        return len(self.queue)
    
    def get_failed_queue(self):
        """Get failed job queue"""
        from rq.queue import FailedJobRegistry
        return FailedJobRegistry(queue=self.queue)
    
    def clear_queue(self):
        """Clear queue"""
        self.queue.empty()


# Global task queue instance
_task_queue: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """Get global task queue instance"""
    global _task_queue
    if _task_queue is None:
        _task_queue = TaskQueue()
    return _task_queue

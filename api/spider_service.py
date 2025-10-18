"""
爬虫服务类 - 集成API与任务系统
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

from tasks.manager import TaskManager
from tasks.models import SpiderTask
from config import Config
from tasks.models import TaskStatus, TaskType
from .models import (
    SpiderTaskRequest, SpiderResponse, 
    TaskInfo
)

class SpiderService:
    """爬虫服务类 - 现在只负责创建任务，不直接执行爬取"""
    
    def __init__(self, tasks_dir: str = None) -> None:
        if tasks_dir is None:
            tasks_dir = Config.DEFAULT_TASKS_DIR
        self.task_manager = TaskManager(tasks_dir)
    
    async def crawl_single(self, request: SpiderTaskRequest) -> SpiderResponse:
        """创建单个URL爬取任务"""
        try:
            # 创建任务
            task = SpiderTask.create_single_task(
                url=request.url,
                spider_name=request.spider_name,
                method=request.method.value,
                timeout=request.timeout,
                max_retries=request.max_retries,
                delay=request.delay
            )
            
            # 保存任务
            task_id = self.task_manager.create_task(task)
            
            # 返回任务创建成功的响应
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
                error_message=f"创建任务失败: {str(e)}"
            )
    
    def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务状态"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return None
        
        # 转换为API模型
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
        """获取任务结果"""
        task = self.task_manager.get_task(task_id)
        if not task or task.status != TaskStatus.COMPLETED:
            return None
        
        # 构建单个任务结果响应
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
    
    def close(self) -> None:
        """关闭服务"""
        pass

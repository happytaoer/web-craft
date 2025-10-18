"""
API Routes - FastAPI route definitions and request handling
"""
import time
import platform
import psutil
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from api.models import (
    SpiderTaskRequest, SpiderResponse,
    TaskInfo, ApiResponse, HealthCheck
)
from api.spider_service import SpiderService

# Create router
router = APIRouter()

# Global service instance
spider_service = SpiderService()

# Service startup time
start_time = time.time()


def create_api_response(success: bool, message: str, data: Any = None, 
                       error_code: str = None) -> ApiResponse:
    """Create unified API response"""
    return ApiResponse(
        success=success,
        message=message,
        data=data,
        error_code=error_code,
        timestamp=datetime.now().isoformat()
    )


@router.get("/health", response_model=ApiResponse, summary="Health Check")
async def health_check() -> ApiResponse:
    """
    Health check endpoint
    
    Returns service status, version information and system information
    """
    try:
        uptime = time.time() - start_time
        
        # Get system information
        system_info: Dict[str, Any] = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent
        }
        
        health_data = HealthCheck(
            status="healthy",
            version="1.0.0",
            uptime=uptime,
            system_info=system_info
        )
        
        return create_api_response(
            success=True,
            message="Service running normally",
            data=health_data.model_dump()
        )
        
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Health check failed: {str(e)}",
            error_code="HEALTH_CHECK_ERROR"
        )


@router.post("/crawl/single", response_model=ApiResponse, summary="Single URL Crawling (Async)")
async def crawl_single_url(request: SpiderTaskRequest) -> ApiResponse:
    """
    Crawl single URL (async task)
    
    Create a single URL crawling task and return task ID. Task will be processed by background executor.
    
    - **url**: Target URL
    - **method**: HTTP method (GET, POST, etc.)
    - **headers**: Custom request headers
    - **timeout**: Timeout duration
    - **max_retries**: Maximum retry count
    - **delay**: Request delay
    
    Returns task ID, can query task status via /task/{task_id}/status
    """
    try:
        result: SpiderResponse = await spider_service.crawl_single(request)
        
        return create_api_response(
            success=result.success,
            message="Task created" if result.success else "Task creation failed",
            data=result.model_dump()
        )
        
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Crawling exception: {str(e)}",
            error_code="CRAWL_ERROR"
        )

@router.get("/task/{task_id}/status", response_model=ApiResponse, summary="Query Task Status")
async def get_task_status(task_id: str) -> ApiResponse:
    """
    Query task status
    
    - **task_id**: Task ID
    """
    try:
        task_info: TaskInfo = spider_service.get_task_status(task_id)
        
        if not task_info:
            return create_api_response(
                success=False,
                message="Task does not exist",
                error_code="TASK_NOT_FOUND"
            )
        
        return create_api_response(
            success=True,
            message="Task status retrieved successfully",
            data=task_info.model_dump()
        )
        
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Failed to query task status: {str(e)}",
            error_code="TASK_STATUS_ERROR"
        )


@router.get("/task/{task_id}/result", response_model=ApiResponse, summary="Get Task Result")
async def get_task_result(task_id: str) -> ApiResponse:
    """
    Get task result
    
    - **task_id**: Task ID
    """
    try:
        task_info: TaskInfo = spider_service.get_task_status(task_id)
        
        if not task_info:
            return create_api_response(
                success=False,
                message="Task does not exist",
                error_code="TASK_NOT_FOUND"
            )
        
        if task_info.status != "completed":
            return create_api_response(
                success=False,
                message=f"Task not completed, current status: {task_info.status}",
                error_code="TASK_NOT_COMPLETED"
            )
        
        result: SpiderResponse = spider_service.get_task_result(task_id)
        
        if not result:
            return create_api_response(
                success=False,
                message="Task result does not exist",
                error_code="RESULT_NOT_FOUND"
            )
        
        return create_api_response(
            success=True,
            message="Task result retrieved successfully",
            data=result.model_dump()
        )
        
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Failed to get task result: {str(e)}",
            error_code="TASK_RESULT_ERROR"
        )


@router.get("/spiders", response_model=ApiResponse, summary="List Available Spiders")
async def list_spiders() -> ApiResponse:
    """
    List all available spiders
    
    Returns a list of all registered spiders with their names and class names.
    """
    try:
        spiders = spider_service.get_available_spiders()
        
        return create_api_response(
            success=True,
            message="Available spiders retrieved successfully",
            data={
                "spiders": spiders,
                "count": len(spiders)
            }
        )
        
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Failed to retrieve spiders: {str(e)}",
            error_code="SPIDERS_LIST_ERROR"
        )


@router.get("/", summary="API Root Path")
async def root() -> Dict[str, str]:
    """
    API root path
    """
    return {
        "message": "Web-Craft API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

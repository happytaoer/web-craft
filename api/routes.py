"""
API Routes - FastAPI route definitions and request handling
"""
import time
import platform
import psutil
import httpx
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from api.models import (
    SpiderTaskRequest, SpiderResponse,
    ApiResponse, HealthCheck,
    CreateSpiderRequest, CreateSpiderResponse,
    DeleteSpiderRequest, DeleteSpiderResponse,
    GetSpiderCodeResponse, EditSpiderRequest, EditSpiderResponse
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
    
    Returns crawling results immediately with task ID for reference.
    """
    try:
        result: SpiderResponse = spider_service.crawl_single(request)
        
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


@router.post("/crawl/debug", response_model=ApiResponse, summary="Single URL Crawling (Debug Mode)")
async def crawl_single_debug(request: SpiderTaskRequest) -> ApiResponse:
    """
    Crawl single URL in debug mode (synchronous execution)
    
    Execute spider immediately and return the extracted data. This is useful for:
    - Testing and debugging spiders
    - Quick data extraction without task queue
    - Development and prototyping
    
    **Note**: This endpoint executes synchronously and may take longer to respond.
    For production use, prefer the `/crawl/single` endpoint which uses async task queue.
    
    - **spider_name**: Spider module name to use
    - **timeout**: Request timeout (optional, defaults to 30 seconds)
    - **params**: URL parameters (optional)
    - **data**: POST data (optional)
    
    Returns the extracted data immediately along with crawling metadata.
    """
    try:
        result: SpiderResponse = spider_service.crawl_single_debug(request)
        
        return create_api_response(
            success=result.success,
            message="Debug crawl completed" if result.success else "Debug crawl failed",
            data=result.model_dump()
        )
        
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Debug crawl exception: {str(e)}",
            error_code="DEBUG_CRAWL_ERROR"
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


@router.post("/spiders/create", response_model=ApiResponse, summary="Create New Spider")
async def create_spider(request: CreateSpiderRequest) -> ApiResponse:
    """
    Create a new spider
    
    Create a new spider file in the spiders directory with the provided code.
    
    - **spider_name**: Name of the spider (will be used as filename)
    - **spider_code**: Complete Python code for the spider
    
    Returns the created spider information including file path.
    """
    try:
        result: CreateSpiderResponse = spider_service.create_spider(
            spider_name=request.spider_name,
            spider_code=request.spider_code
        )
        
        return create_api_response(
            success=True,
            message=result.message,
            data=result.model_dump()
        )
        
    except ValueError as e:
        error_msg = str(e)
        # Check if this is a validation error
        if "Spider validation failed" in error_msg:
            import ast
            try:
                # Extract validation errors from error message
                error_list_str = error_msg.split("Spider validation failed: ")[1]
                validation_errors = ast.literal_eval(error_list_str)
                return create_api_response(
                    success=False,
                    message="Spider validation failed",
                    error_code="VALIDATION_ERROR",
                    data={"validation_errors": validation_errors}
                )
            except:
                pass
        return create_api_response(
            success=False,
            message=error_msg,
            error_code="INVALID_SPIDER_NAME"
        )
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Failed to create spider: {str(e)}",
            error_code="SPIDER_CREATION_ERROR"
        )


@router.get("/spiders/{spider_name}/code", response_model=ApiResponse, summary="Get Spider Code")
async def get_spider_code(spider_name: str) -> ApiResponse:
    """
    Get spider code
    
    Retrieve the Python code of a spider.
    
    - **spider_name**: Name of the spider
    
    Returns the spider code.
    """
    try:
        result: GetSpiderCodeResponse = spider_service.get_spider_code(spider_name)
        
        return create_api_response(
            success=True,
            message="Spider code retrieved successfully",
            data=result.model_dump()
        )
        
    except ValueError as e:
        return create_api_response(
            success=False,
            message=str(e),
            error_code="INVALID_SPIDER_NAME"
        )
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Failed to get spider code: {str(e)}",
            error_code="SPIDER_CODE_ERROR"
        )


@router.put("/spiders/{spider_name}", response_model=ApiResponse, summary="Edit Spider")
async def edit_spider(spider_name: str, request: EditSpiderRequest) -> ApiResponse:
    """
    Edit an existing spider
    
    Update the Python code of an existing spider.
    
    - **spider_name**: Name of the spider to edit (must match request body)
    - **spider_code**: Updated Python code for the spider
    
    Returns the edit result.
    """
    try:
        # Verify spider_name matches
        if spider_name != request.spider_name:
            raise ValueError("Spider name in URL does not match request body")
        
        result: EditSpiderResponse = spider_service.edit_spider(
            spider_name=request.spider_name,
            spider_code=request.spider_code
        )
        
        return create_api_response(
            success=True,
            message=result.message,
            data=result.model_dump()
        )
        
    except ValueError as e:
        error_msg = str(e)
        # Check if this is a validation error
        if "Spider validation failed" in error_msg:
            import ast
            try:
                # Extract validation errors from error message
                error_list_str = error_msg.split("Spider validation failed: ")[1]
                validation_errors = ast.literal_eval(error_list_str)
                return create_api_response(
                    success=False,
                    message="Spider validation failed",
                    error_code="VALIDATION_ERROR",
                    data={"validation_errors": validation_errors}
                )
            except:
                pass
        return create_api_response(
            success=False,
            message=error_msg,
            error_code="INVALID_SPIDER_EDIT"
        )
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Failed to edit spider: {str(e)}",
            error_code="SPIDER_EDIT_ERROR"
        )


@router.delete("/spiders/{spider_name}", response_model=ApiResponse, summary="Delete Spider")
async def delete_spider(spider_name: str) -> ApiResponse:
    """
    Delete a spider
    
    Delete a spider file from the spiders directory.
    
    - **spider_name**: Name of the spider to delete
    
    **Note**: Protected spiders (ip, hackernews) cannot be deleted.
    
    Returns the deletion result.
    """
    try:
        result: DeleteSpiderResponse = spider_service.delete_spider(spider_name)
        
        return create_api_response(
            success=True,
            message=result.message,
            data=result.model_dump()
        )
        
    except ValueError as e:
        return create_api_response(
            success=False,
            message=str(e),
            error_code="INVALID_SPIDER_DELETE"
        )
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Failed to delete spider: {str(e)}",
            error_code="SPIDER_DELETION_ERROR"
        )


@router.get("/fetch-url", response_model=ApiResponse, summary="Fetch URL Content")
async def fetch_url(url: str) -> ApiResponse:
    """
    Fetch HTML content from a URL
    
    Args:
        url: Target URL to fetch
        
    Returns:
        ApiResponse with HTML content and metadata
    """
    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            html_content = response.text
            
            # 提取页面标题
            import re
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else '无标题'
            
            return create_api_response(
                success=True,
                message="URL content fetched successfully",
                data={
                    "url": str(response.url),
                    "status_code": response.status_code,
                    "title": title,
                    "html_content": html_content,
                    "content_length": len(html_content),
                    "encoding": response.encoding or 'utf-8',
                    "headers": dict(response.headers)
                }
            )
    except httpx.HTTPStatusError as e:
        return create_api_response(
            success=False,
            message=f"HTTP error: {e.response.status_code}",
            error_code="HTTP_ERROR"
        )
    except httpx.TimeoutException:
        return create_api_response(
            success=False,
            message="Request timeout",
            error_code="TIMEOUT_ERROR"
        )
    except Exception as e:
        return create_api_response(
            success=False,
            message=f"Failed to fetch URL: {str(e)}",
            error_code="FETCH_ERROR"
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

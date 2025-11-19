"""
Spider Service Class - Integrates API with RQ Task Queue
"""
import os
import re
from pathlib import Path
from typing import Dict
from tasks.queue import get_task_queue
from tasks.worker_tasks import execute_spider_task
from spiders.core.spider_loader import SpiderLoader
from spiders.core.spider_validator import SpiderValidator
from .models import (
    SpiderTaskRequest, SpiderResponse, CreateSpiderResponse, DeleteSpiderResponse,
    GetSpiderCodeResponse, EditSpiderResponse, ValidationErrorDetail
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
    
    def crawl_single_debug(self, request: SpiderTaskRequest) -> SpiderResponse:
        """Execute spider synchronously for debugging (returns result immediately)"""
        try:
            # Get spider instance
            spider = self.spider_loader.get_spider(request.spider_name)
            if not spider:
                raise ValueError(f"Spider '{request.spider_name}' not found")
            
            # Execute spider synchronously
            result = spider.crawl_single(request)
            
            # Convert SpiderResult to SpiderResponse
            return SpiderResponse(
                url=result.url,
                status_code=result.status_code,
                success=result.success,
                content_length=result.content_length,
                encoding=result.encoding,
                headers=result.headers,
                request_headers=result.request_headers,
                response_time=result.response_time,
                extracted_data=result.extracted_data,
                error_message=result.error_message,
                task_id=None  # No task ID for debug mode
            )
            
        except Exception as e:
            return SpiderResponse(
                url=f"<{request.spider_name}>",
                status_code=500,
                success=False,
                content_length=0,
                encoding="utf-8",
                headers={},
                error_message=f"Debug execution failed: {str(e)}"
            )
    
    def get_available_spiders(self) -> Dict[str, str]:
        """Get list of available spiders"""
        return self.spider_loader.list_spiders()
    
    def create_spider(self, spider_name: str, spider_code: str) -> CreateSpiderResponse:
        """Create a new spider file"""
        # Validate spider name
        if not spider_name or not re.match(r'^[a-z][a-z0-9_]*$', spider_name):
            raise ValueError(
                "Spider name must start with a lowercase letter and contain only "
                "lowercase letters, numbers, and underscores"
            )
        
        # Validate spider code before saving
        validation_result = SpiderValidator.validate_all(spider_code, spider_name)
        if not validation_result.success:
            # Convert validation errors to exception with structured data
            error_details = [
                {
                    "type": err.type,
                    "message": err.message,
                    "line": err.line,
                    "detail": err.detail
                }
                for err in validation_result.errors
            ]
            raise ValueError(f"Spider validation failed: {error_details}")
        
        # Get spiders directory path
        spiders_dir = Path(__file__).parent.parent / "spiders" / "spiders"
        if not spiders_dir.exists():
            raise ValueError(f"Spiders directory not found: {spiders_dir}")
        
        # Create file path
        file_name = f"{spider_name}.py"
        file_path = spiders_dir / file_name
        
        # Check if file already exists
        if file_path.exists():
            raise ValueError(f"Spider '{spider_name}' already exists")
        
        # Write spider code to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(spider_code)
            
            # Reload spider loader to include new spider
            self.spider_loader.reload_spiders()
            
            return CreateSpiderResponse(
                spider_name=spider_name,
                message=f"Spider '{spider_name}' created successfully"
            )
        except Exception as e:
            # Clean up file if write failed
            if file_path.exists():
                file_path.unlink()
            raise Exception(f"Failed to write spider file: {str(e)}")
    
    def delete_spider(self, spider_name: str) -> DeleteSpiderResponse:
        """Delete a spider file"""
        # Validate spider name
        if not spider_name or not re.match(r'^[a-z][a-z0-9_]*$', spider_name):
            raise ValueError(
                "Invalid spider name format"
            )
        
        # Check if spider exists in loader
        spider_class = self.spider_loader._spiders.get(spider_name)
        if not spider_class:
            raise ValueError(f"Spider '{spider_name}' not found")
        
        # Prevent deletion of default spiders
        protected_spiders = ['ip', 'hackernews']
        if spider_name in protected_spiders:
            raise ValueError(f"Cannot delete protected spider '{spider_name}'")
        
        # Get spiders directory path
        spiders_dir = Path(__file__).parent.parent / "spiders" / "spiders"
        if not spiders_dir.exists():
            raise ValueError(f"Spiders directory not found: {spiders_dir}")
        
        # Find the actual file by searching for the spider class module
        module_name = spider_class.__module__.split('.')[-1]  # Get module name from class
        file_name = f"{module_name}.py"
        file_path = spiders_dir / file_name
        
        # Check if file exists
        if not file_path.exists():
            raise ValueError(f"Spider file '{file_name}' not found")
        
        # Delete the file
        try:
            file_path.unlink()
            
            # Reload spider loader to update spider list
            self.spider_loader.reload_spiders()
            
            return DeleteSpiderResponse(
                spider_name=spider_name,
                message=f"Spider '{spider_name}' deleted successfully"
            )
        except Exception as e:
            raise Exception(f"Failed to delete spider file: {str(e)}")
    
    def get_spider_code(self, spider_name: str) -> GetSpiderCodeResponse:
        """Get spider code from file"""
        # Validate spider name
        if not spider_name or not re.match(r'^[a-z][a-z0-9_]*$', spider_name):
            raise ValueError("Invalid spider name format")
        
        # Check if spider exists in loader
        spider_class = self.spider_loader._spiders.get(spider_name)
        if not spider_class:
            raise ValueError(f"Spider '{spider_name}' not found")
        
        # Get spiders directory path
        spiders_dir = Path(__file__).parent.parent / "spiders" / "spiders"
        if not spiders_dir.exists():
            raise ValueError(f"Spiders directory not found: {spiders_dir}")
        
        # Find the actual file by searching for the spider class module
        module_name = spider_class.__module__.split('.')[-1]
        file_name = f"{module_name}.py"
        file_path = spiders_dir / file_name
        
        # Check if file exists
        if not file_path.exists():
            raise ValueError(f"Spider file '{file_name}' not found")
        
        # Read spider code
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                spider_code = f.read()
            
            return GetSpiderCodeResponse(
                spider_name=spider_name,
                spider_code=spider_code
            )
        except Exception as e:
            raise Exception(f"Failed to read spider file: {str(e)}")
    
    def edit_spider(self, spider_name: str, spider_code: str) -> EditSpiderResponse:
        """Edit an existing spider file"""
        # Validate spider name
        if not spider_name or not re.match(r'^[a-z][a-z0-9_]*$', spider_name):
            raise ValueError("Invalid spider name format")
        
        # Validate spider code before saving
        validation_result = SpiderValidator.validate_all(spider_code, spider_name)
        if not validation_result.success:
            # Convert validation errors to exception with structured data
            error_details = [
                {
                    "type": err.type,
                    "message": err.message,
                    "line": err.line,
                    "detail": err.detail
                }
                for err in validation_result.errors
            ]
            raise ValueError(f"Spider validation failed: {error_details}")
        
        # Check if spider exists in loader
        spider_class = self.spider_loader._spiders.get(spider_name)
        if not spider_class:
            raise ValueError(f"Spider '{spider_name}' not found")
        
        # Get spiders directory path
        spiders_dir = Path(__file__).parent.parent / "spiders" / "spiders"
        if not spiders_dir.exists():
            raise ValueError(f"Spiders directory not found: {spiders_dir}")
        
        # Find the actual file by searching for the spider class module
        module_name = spider_class.__module__.split('.')[-1]
        file_name = f"{module_name}.py"
        file_path = spiders_dir / file_name
        
        # Check if file exists
        if not file_path.exists():
            raise ValueError(f"Spider file '{file_name}' not found")
        
        # Write updated spider code to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(spider_code)
            
            # Reload spider loader to update spider
            self.spider_loader.reload_spiders()
            
            return EditSpiderResponse(
                spider_name=spider_name,
                message=f"Spider '{spider_name}' updated successfully"
            )
        except Exception as e:
            raise Exception(f"Failed to update spider file: {str(e)}")
    
    def close(self) -> None:
        """Close service"""
        pass

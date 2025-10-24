"""
API Data Models - Define data structures for requests and responses
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum
from dataclasses import dataclass


class HttpMethod(str, Enum):
    """HTTP request method enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class SpiderTaskRequest(BaseModel):
    """Spider task request model"""
    url: HttpUrl = Field(..., description="Target URL")
    spider_name: str = Field(default="default", description="Spider module name")
    method: HttpMethod = Field(default=HttpMethod.GET, description="HTTP request method")
    params: Optional[Dict[str, Any]] = Field(default=None, description="URL parameters")
    data: Optional[Dict[str, Any]] = Field(default=None, description="POST data")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout (seconds)")
    use_proxy: bool = Field(default=False, description="Whether to use proxy")
    
    @validator('url')
    def validate_url(cls, v: HttpUrl) -> str:
        """Validate URL format"""
        return str(v)

class SpiderResponse(BaseModel):
    """Spider response data model"""
    url: str = Field(..., description="Request URL")
    status_code: int = Field(..., description="HTTP status code")
    success: bool = Field(..., description="Whether successful")
    content_length: int = Field(default=0, description="Content length")
    encoding: str = Field(default="utf-8", description="Encoding format")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")
    response_time: float = Field(default=0.0, description="Response time (seconds)")
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, description="Extracted data")
    error_message: Optional[str] = Field(default=None, description="Error message")
    task_id: Optional[str] = Field(default=None, description="Task ID")


class ApiResponse(BaseModel):
    """Unified API response model"""
    success: bool = Field(..., description="Whether successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    error_code: Optional[str] = Field(default=None, description="Error code")
    timestamp: str = Field(..., description="Response timestamp")


class HealthCheck(BaseModel):
    """Health check model"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Version number")
    uptime: float = Field(..., description="Uptime (seconds)")
    system_info: Dict[str, Any] = Field(..., description="System information")

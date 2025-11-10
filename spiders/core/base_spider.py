"""
Base Spider Class - Define common interfaces and behaviors for all spiders
"""
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from api.models import SpiderTaskRequest
from worker.spider_engine import SpiderEngine


@dataclass
class SpiderResult:
    """Spider result data model"""
    url: str
    status_code: int
    success: bool
    content: str
    content_length: int
    encoding: str
    headers: Dict[str, str]
    response_time: float
    error_message: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class BaseSpider(ABC):
    """
    Base spider abstract class
    
    All custom spiders should inherit from this class and implement necessary methods
    """
    
    # Default start URL - subclasses should override this
    start_url = None
    
    def __init__(self):
        """Initialize spider"""
        self.spider_engine = SpiderEngine()
        self.name = self.__class__.__name__.lower()
    
    def pre_request(self, request: SpiderTaskRequest) -> SpiderTaskRequest:
        """
        Request pre-processing, can modify request parameters
        
        Args:
            request: Original request object
            
        Returns:
            Modified request object
        """
        return request

    def crawl_single(self, request: SpiderTaskRequest) -> SpiderResult:
        """
        Crawl single URL
        
        Args:
            request: Crawl request
            
        Returns:
            Crawl result
        """
        # Use spider's start_url
        if not self.start_url:
            raise ValueError(f"Spider '{self.name}' has no start_url configured")
        request.url = self.start_url
        
        # Request pre-processing
        processed_request = self.pre_request(request)
        
        start_time = time.time()
        
        try:
            # Use spider engine to execute request
            response = self.spider_engine.fetch(processed_request)
            
            if response and response.success:
                # Call subclass parse method, pass in raw content
                extracted_data = self.parse(
                    raw_content=response.content,
                    url=response.url,
                    headers=response.headers
                )
                
                result = SpiderResult(
                    url=response.url,
                    status_code=response.status_code,
                    success=True,
                    content=response.content,
                    content_length=response.content_length,
                    encoding=response.encoding,
                    headers=response.headers,
                    response_time=time.time() - start_time,
                    extracted_data=extracted_data
                )
            else:
                # response is None or failed
                if response:
                    result = SpiderResult(
                        url=response.url,
                        status_code=response.status_code,
                        success=False,
                        content=response.content or "",
                        content_length=response.content_length,
                        encoding=response.encoding,
                        headers=response.headers,
                        response_time=time.time() - start_time,
                        error_message=response.error_message
                    )
                else:
                    result = SpiderResult(
                        url=str(processed_request.url),
                        status_code=0,
                        success=False,
                        content="",
                        content_length=0,
                        encoding="",
                        headers={},
                        response_time=time.time() - start_time,
                        error_message="Request failed, no response received"
                    )
                
        except Exception as e:
            result = SpiderResult(
                url=str(processed_request.url),
                status_code=0,
                success=False,
                content="",
                content_length=0,
                encoding="",
                headers={},
                response_time=time.time() - start_time,
                error_message=str(e)
            )
        
        # Post processing
        return self.post_process(result)
    
    @abstractmethod
    def parse(self, raw_content: str, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse response content and extract data
        
        Args:
            raw_content: Raw HTML/text content
            url: Requested URL
            headers: Response header information
            
        Returns:
            Extracted data dictionary
        """
        pass

    def post_process(self, result: SpiderResult) -> SpiderResult:
        """
        Post processing, can modify crawl result
        
        Args:
            result: Original crawl result
            
        Returns:
            Modified crawl result
        """
        return result

"""
Worker Layer - Spider Core Engine
Responsible for executing actual web scraping and data extraction
"""
from typing import Dict, Optional
import requests
from fake_useragent import UserAgent

from api.models import SpiderTaskRequest
from config import config


class SpiderResponse:
    """Spider response data class"""
    
    def __init__(self, url: str, status_code: int, content: str, 
                 headers: Dict[str, str], encoding: str = 'utf-8', 
                 success: bool = None, error_message: str = None):
        self.url = url
        self.status_code = status_code
        self.content = content
        self.headers = headers
        self.encoding = encoding
        self.success = success if success is not None else (200 <= status_code < 400)
        self.error_message = error_message
        self.content_length = len(content) if content else 0

class SpiderEngine:
    """Spider Engine"""

    def __init__(self):
        self.ua = UserAgent()
    
    
    def fetch(self, request: SpiderTaskRequest) -> Optional[SpiderResponse]:
        """Synchronous web scraping using requests"""
        try:
            # Prepare request parameters
            headers = {}
            headers['User-Agent'] = self.ua.random
            
            response = requests.request(
                method=request.method.value,
                url=str(request.url),
                headers=headers,
                params=request.params,
                data=request.data,
                timeout=request.timeout
            )
            
            spider_response = SpiderResponse(
                url=response.url,
                status_code=response.status_code,
                content=response.text,
                headers=dict(response.headers),
                encoding=response.encoding or 'utf-8',
                success=True
            )
            
            return spider_response
                    
        except requests.RequestException as e:
            print(f"Request failed {request.url}: {e}")
            return SpiderResponse(
                url=str(request.url),
                status_code=0,
                content="",
                headers={},
                encoding="utf-8",
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            print(f"Unknown error {request.url}: {e}")
            return SpiderResponse(
                url=str(request.url),
                status_code=0,
                content="",
                headers={},
                encoding="utf-8",
                success=False,
                error_message=str(e)
            )
    
    def close(self):
        """Close resources (not needed for requests)"""
        pass

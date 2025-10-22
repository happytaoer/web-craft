"""
Worker Layer - Spider Core Engine
Responsible for executing actual web scraping and data extraction
"""
import asyncio
from typing import Dict, Optional
import aiohttp
from fake_useragent import UserAgent

from input.parameter_handler import SpiderRequest
from config import Config


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
    
    
    async def fetch_async(self, request: SpiderRequest) -> Optional[SpiderResponse]:
        """Asynchronous web scraping"""
        try:
            # Prepare request parameters - use default headers
            headers = {}
            headers['User-Agent'] = self.ua.random
            
            timeout = aiohttp.ClientTimeout(total=request.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method=request.method,
                    url=request.url,
                    headers=headers,
                    params=request.params,
                    data=request.data
                ) as response:
                    content = await response.text()
                    
                    spider_response = SpiderResponse(
                        url=str(response.url),
                        status_code=response.status,
                        content=content,
                        headers=dict(response.headers),
                        encoding=response.charset or 'utf-8',
                        success=True
                    )
                    
                    return spider_response
                    
        except aiohttp.ClientError as e:
            print(f"Async request failed {request.url}: {e}")
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
    
    async def fetch_with_retry(self, request: SpiderRequest) -> Optional[SpiderResponse]:
        """Fetch with retry (async)"""
        for attempt in range(request.max_retries + 1):
            try:
                response = await self.fetch_async(request)
                if response and response.status_code == 200:
                    return response
                
                if attempt < request.max_retries:
                    print(f"Retry {attempt + 1}/{request.max_retries} - {request.url}")
                    await asyncio.sleep(request.delay * (attempt + 1))
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < request.max_retries:
                    await asyncio.sleep(request.delay * (attempt + 1))
        
        return None
    
    def close(self):
        """Close resources (no longer needed for async-only)"""
        pass

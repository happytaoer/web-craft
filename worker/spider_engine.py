"""
Worker Layer - Spider Core Engine
Responsible for executing actual web scraping and data extraction
"""
import asyncio
import time
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
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
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def fetch_sync(self, request: SpiderRequest) -> Optional[SpiderResponse]:
        """Synchronous web scraping"""
        try:
            # Prepare request parameters - use default headers
            headers = Config.DEFAULT_HEADERS.copy()
            headers['User-Agent'] = self.ua.random
            
            # Send request
            response = self.session.request(
                method=request.method,
                url=request.url,
                headers=headers,
                params=request.params,
                data=request.data,
                timeout=request.timeout
            )
            
            response.raise_for_status()
            
            # Create response object
            spider_response = SpiderResponse(
                url=str(response.url),
                status_code=response.status_code,
                content=response.text,
                headers=dict(response.headers),
                encoding=response.encoding or 'utf-8',
                success=True
            )
            
            return spider_response
            
        except requests.RequestException as e:
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
    
    async def fetch_async(self, request: SpiderRequest) -> Optional[SpiderResponse]:
        """Asynchronous web scraping"""
        try:
            # Prepare request parameters - use default headers
            headers = Config.DEFAULT_HEADERS.copy()
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
    
    def fetch_with_retry(self, request: SpiderRequest) -> Optional[SpiderResponse]:
        """Fetch with retry"""
        for attempt in range(request.max_retries + 1):
            try:
                response = self.fetch_sync(request)
                if response and response.status_code == 200:
                    return response
                
                if attempt < request.max_retries:
                    print(f"Retry {attempt + 1}/{request.max_retries} - {request.url}")
                    time.sleep(request.delay * (attempt + 1))
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < request.max_retries:
                    time.sleep(request.delay * (attempt + 1))
        
        return None
    
    def close(self):
        """Close session"""
        if self.session:
            self.session.close()

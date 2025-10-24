"""
Input layer - parameter receiving and processing module
Responsible for receiving and validating spider task input parameters
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

@dataclass
class SpiderRequest:
    """spider request parameter data class"""
    url: str
    method: str = "GET"
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: int = 30
    max_retries: int = 3
    use_proxy: bool = False

    def __post_init__(self):
        """initialize validation"""
        if not self.url:
            raise ValueError("URL cannot be empty")
        
        if not self._is_valid_url(self.url):
            raise ValueError(f"Invalid URL: {self.url}")
        

        if self.params is None:
            self.params = {}
            
        if self.data is None:
            self.data = {}
    
    def _is_valid_url(self, url: str) -> bool:
        """validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
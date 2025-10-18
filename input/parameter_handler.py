"""
Input层 - 参数接收和处理模块
负责接收和验证爬虫任务的输入参数
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

@dataclass
class SpiderRequest:
    """爬虫请求参数数据类"""
    url: str
    method: str = "GET"
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: int = 30
    max_retries: int = 3
    delay: float = 1.0
    use_proxy: bool = False
    render_js: bool = False
    
    def __post_init__(self):
        """初始化后的验证"""
        if not self.url:
            raise ValueError("URL不能为空")
        
        if not self._is_valid_url(self.url):
            raise ValueError(f"无效的URL: {self.url}")
        

        if self.params is None:
            self.params = {}
            
        if self.data is None:
            self.data = {}
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
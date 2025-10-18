"""
默认爬虫 - 通用网页内容爬取
"""
from typing import Dict, Any
from .base_spider import BaseSpider


class DefaultSpider(BaseSpider):
    """
    默认爬虫实现
    
    提供基本的网页内容提取功能：
    - 标题提取
    - 文本内容提取
    - 链接提取
    - 图片提取
    """
    
    def parse(self, raw_content: str, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        解析网页内容，提取基本信息
        
        Args:
            raw_content: 原始HTML/文本内容
            url: 请求的URL
            headers: 响应头信息
            
        Returns:
            提取的数据字典
        """
        return raw_content

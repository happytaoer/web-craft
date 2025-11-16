"""
Default spider - General web page content crawling
"""
from typing import Dict, Any
from ..core.base_spider import BaseSpider


class DefaultSpider(BaseSpider):
    """
    Default spider implementation
    """
    
    name = "default"
    
    def parse(self, raw_content: str, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse web page content and extract basic information
        
        Args:
            raw_content: original HTML/text content
            url: requested URL
            headers: response header information
            
        Returns:
            extracted data dictionary
        """
        return raw_content

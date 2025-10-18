"""
Configuration File - Global configuration for spider system
"""
import os
from typing import Dict, List


class Config:
    """Spider system configuration class"""
    
    # Basic configuration
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_DELAY = 1.0
    
    # Task configuration
    DEFAULT_TASKS_DIR = "data/tasks"
    
    # Request headers configuration
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Proxy configuration
    PROXY_ENABLED = False
    PROXY_LIST = [
        # 'http://proxy1:port',
        # 'http://proxy2:port',
    ]
    
    # Concurrency configuration
    MAX_CONCURRENT_REQUESTS = 10
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "spider.log"
    
    # Database configuration (optional)
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    
    # Cache configuration
    CACHE_ENABLED = False
    CACHE_DIR = "cache"
    CACHE_EXPIRE_HOURS = 24
    
    # Security configuration
    RESPECT_ROBOTS_TXT = True
    MIN_REQUEST_INTERVAL = 0.5  # Minimum request interval (seconds)
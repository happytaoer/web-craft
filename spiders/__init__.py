"""
Spider Module Package - Contains various specialized spider implementations
"""
from .core.base_spider import BaseSpider, SpiderResult
from .core.spider_loader import SpiderLoader, spider_loader

__all__ = ['BaseSpider', 'SpiderResult', 'SpiderLoader', 'spider_loader']

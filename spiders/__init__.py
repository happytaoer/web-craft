"""
Spider Module Package - Contains various specialized spider implementations
"""
from .core.base_spider import BaseSpider, SpiderResult
from .spiders.default_spider import DefaultSpider
from .core.spider_loader import SpiderLoader, spider_loader

__all__ = ['BaseSpider', 'SpiderResult', 'DefaultSpider', 'SpiderLoader', 'spider_loader']

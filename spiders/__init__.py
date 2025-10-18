"""
Spider Module Package - Contains various specialized spider implementations
"""
from .base_spider import BaseSpider, SpiderResult
from .default_spider import DefaultSpider
from .spider_loader import SpiderLoader, spider_loader

__all__ = ['BaseSpider', 'SpiderResult', 'DefaultSpider', 'SpiderLoader', 'spider_loader']

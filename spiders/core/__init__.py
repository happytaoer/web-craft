"""
Spider Core Framework - Framework components for the spider system
"""

from .base_spider import BaseSpider, SpiderResult
from .spider_loader import SpiderLoader, spider_loader

__all__ = [
    'BaseSpider',
    'SpiderResult',
    'SpiderLoader',
    'spider_loader',
]

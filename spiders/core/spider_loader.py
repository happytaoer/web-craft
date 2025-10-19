"""
Spider Loader - Dynamically load and manage spider modules
"""
import importlib
from typing import Dict, Type, Optional
from pathlib import Path

from .base_spider import BaseSpider


class SpiderLoader:
    """
    Spider Loader
    
    Responsible for dynamically loading and managing different spider modules
    """
    
    def __init__(self):
        """Initialize spider loader"""
        self._spiders: Dict[str, Type[BaseSpider]] = {}
        self._spider_instances: Dict[str, BaseSpider] = {}
        self._discover_custom_spiders()
    
    def _discover_custom_spiders(self):
        """Automatically discover custom spiders"""
        # Look for spiders in the spiders/spiders directory
        spiders_dir = Path(__file__).parent.parent / "spiders"
        
        if not spiders_dir.exists():
            return
            
        for file_path in spiders_dir.glob("*.py"):
            if file_path.name.startswith('_'):
                continue
            
            module_name = file_path.stem
            try:
                # Dynamically import module from spiders.spiders package
                module = importlib.import_module(f'spiders.spiders.{module_name}')
                
                # Find classes that inherit from BaseSpider
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseSpider) and 
                        attr != BaseSpider):
                        
                        # Generate spider name
                        spider_instance = attr()
                        spider_name = spider_instance.name 
                        if spider_name and spider_name not in self._spiders:
                            self.register_spider(spider_name, attr)
                            
            except Exception as e:
                print(f"Warning: Failed to load spider module {module_name}: {e}")
    
    def register_spider(self, name: str, spider_class: Type[BaseSpider]):
        """
        Register spider class
        
        Args:
            name: Spider name
            spider_class: Spider class
        """
        if not issubclass(spider_class, BaseSpider):
            raise ValueError(f"Spider class {spider_class.__name__} must inherit from BaseSpider")
        
        self._spiders[name] = spider_class
        print(f"Registered spider: {name}")
    
    def get_spider(self, name: str) -> Optional[BaseSpider]:
        """
        Get spider instance
        
        Args:
            name: Spider name
            
        Returns:
            Spider instance, returns None if not exists
        """
        if name not in self._spiders:
            print(f"Warning: Spider '{name}' not found, using default spider")
            name = 'default'
        
        # Use singleton pattern to avoid duplicate instance creation
        if name not in self._spider_instances:
            spider_class = self._spiders[name]
            self._spider_instances[name] = spider_class()
        
        return self._spider_instances[name]
    
    def list_spiders(self) -> Dict[str, str]:
        """
        List all available spiders
        
        Returns:
            Mapping from spider names to class names
        """
        return {name: cls.__name__ for name, cls in self._spiders.items()}
    
    def spider_exists(self, name: str) -> bool:
        """
        Check if spider exists
        
        Args:
            name: Spider name
            
        Returns:
            Whether it exists
        """
        return name in self._spiders
    
    def reload_spiders(self):
        """Reload all spiders"""
        self._spiders.clear()
        self._spider_instances.clear()
        self._discover_custom_spiders()


# Global spider loader instance
spider_loader = SpiderLoader()

"""
Configuration File - Global configuration for spider system
"""
class Config:
    """Spider system configuration class"""
    
    # Basic configuration
    DEFAULT_TIMEOUT = 30
    
    # Task configuration
    DEFAULT_TASKS_DIR = "data/tasks"
    
    # Concurrency configuration
    MAX_CONCURRENT_REQUESTS = 10
"""
Configuration File - Global configuration for spider system
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import tomllib

@dataclass
class SpiderConfig:
    """Spider configuration"""
    timeout: int = 30
    max_retries: int = 3
    delay: float = 1.0


@dataclass
class TasksConfig:
    """Tasks configuration"""
    tasks_dir: str = "data/tasks"


@dataclass
class ConcurrencyConfig:
    """Concurrency configuration"""
    max_concurrent_requests: int = 10


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class Config:
    """Global configuration class"""
    spider: SpiderConfig = field(default_factory=SpiderConfig)
    tasks: TasksConfig = field(default_factory=TasksConfig)
    concurrency: ConcurrencyConfig = field(default_factory=ConcurrencyConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def from_toml(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from TOML file"""
        if config_path is None:
            config_path = Path(__file__).parent / "config.toml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        
        # Create configuration object
        config = cls(
            spider=SpiderConfig(**data.get("spider", {})),
            tasks=TasksConfig(**data.get("tasks", {})),
            concurrency=ConcurrencyConfig(**data.get("concurrency", {})),
            server=ServerConfig(**data.get("server", {})),
            logging=LoggingConfig(**data.get("logging", {})),
        )
        
        return config
    
    def validate(self):
        """Validate configuration"""
        if self.spider.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.spider.max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to 0")
        if self.concurrency.max_concurrent_requests <= 0:
            raise ValueError("max_concurrent_requests must be greater than 0")
        if not (1 <= self.server.port <= 65535):
            raise ValueError("port must be in range 1-65535")


# Global configuration instance (singleton)
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.from_toml()
        _config_instance.validate()
    return _config_instance


# Export global configuration instance
config = get_config()
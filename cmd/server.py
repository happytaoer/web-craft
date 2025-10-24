"""
API server startup command line tool
Supports rich command line parameter configuration
"""
import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.app import run_server
from config import config


def setup_logging(log_level: str, log_file: Optional[str] = None) -> None:
    """Configure logging system"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # File handler (if log file is specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def validate_args(args: argparse.Namespace) -> None:
    """Validate command line arguments"""
    # Validate port range
    if not (1 <= args.port <= 65535):
        raise ValueError(f"Port must be in range 1-65535, current value: {args.port}")
    
    # Validate worker count
    if args.workers < 1:
        raise ValueError(f"Worker count must be greater than 0, current value: {args.workers}")
    
    # Validate log level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if args.log_level.upper() not in valid_levels:
        raise ValueError(f"Invalid log level: {args.log_level}, valid values: {valid_levels}")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="🕷️ Web-Craft API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s                                   # Start with default configuration
  %(prog)s --port 8080 --host 0.0.0.0        # Specify port and host
  %(prog)s --reload --log-level DEBUG        # Development mode with debug logging
  %(prog)s --workers 4                       # Production mode with 4 worker processes
  %(prog)s --config-file custom.env          # Use custom configuration file
        """
    )
    
    # Server configuration
    server_group = parser.add_argument_group('Server Configuration')
    server_group.add_argument(
        '--host', 
        type=str, 
        default='127.0.0.1',
        help='Server host address (default: 127.0.0.1)'
    )
    server_group.add_argument(
        '--port', 
        type=int, 
        default=8000,
        help='Server port (default: 8000)'
    )
    server_group.add_argument(
        '--workers', 
        type=int, 
        default=1,
        help='Number of worker processes, recommended to set to CPU core count in production (default: 1)'
    )
    
    # Development configuration
    dev_group = parser.add_argument_group('Development Configuration')
    dev_group.add_argument(
        '--reload', 
        action='store_true',
        help='Enable auto-reload, automatically restart when code changes (development mode)'
    )
    dev_group.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug mode, show detailed error information'
    )
    
    # Logging configuration
    log_group = parser.add_argument_group('Logging Configuration')
    log_group.add_argument(
        '--log-level', 
        type=str, 
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level (default: INFO)'
    )
    log_group.add_argument(
        '--log-file', 
        type=str,
        help='Log file path, if not specified, output only to console'
    )
    log_group.add_argument(
        '--access-log', 
        action='store_true',
        help='Enable access log recording'
    )
    
    # Security configuration
    security_group = parser.add_argument_group('Security Configuration')
    security_group.add_argument(
        '--cors-origins', 
        type=str, 
        nargs='*',
        default=['*'],
        help='Allowed CORS origins, recommend specifying specific domains in production (default: *)'
    )
    security_group.add_argument(
        '--api-key', 
        type=str,
        help='API access key, when enabled, X-API-Key header is required in requests'
    )
    
    # Configuration file
    config_group = parser.add_argument_group('Configuration File')
    config_group.add_argument(
        '--config-file', 
        type=str,
        help='Environment variable configuration file path (.env format)'
    )
    
    # Other options
    other_group = parser.add_argument_group('Other Options')
    other_group.add_argument(
        '--version', 
        action='version', 
        version='Web-Craft API v1.0.0'
    )
    other_group.add_argument(
        '--check-config', 
        action='store_true',
        help='Check configuration and exit, do not start server'
    )
    
    return parser


def load_config_file(config_file: str) -> None:
    """Load configuration file"""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file does not exist: {config_file}")
    
    try:
        from dotenv import load_dotenv
        load_dotenv(config_file)
        print(f"✅ Configuration file loaded: {config_file}")
    except ImportError:
        print("⚠️  Warning: python-dotenv package is required to support .env configuration files")
        print("   Run: pip install python-dotenv")
    except Exception as e:
        raise ValueError(f"Failed to load configuration file: {e}")


def print_startup_info(args: argparse.Namespace) -> None:
    """Print startup information"""
    print("🕷️ Web-Craft API Server")
    print("=" * 50)
    print(f"📡 Host Address: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"👥 Workers: {args.workers}")
    print(f"🔄 Auto Reload: {'Yes' if args.reload else 'No'}")
    print(f"🐛 Debug Mode: {'Yes' if args.debug else 'No'}")
    print(f"📝 Log Level: {args.log_level}")
    
    if args.log_file:
        print(f"📄 Log File: {args.log_file}")
    
    if args.api_key:
        print(f"🔐 API Key: Enabled")
    
    print("=" * 50)
    print(f"📖 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 ReDoc Documentation: http://{args.host}:{args.port}/redoc")
    print(f"❤️  Health Check: http://{args.host}:{args.port}/api/v1/health")
    print("=" * 50)


def main() -> None:
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Load configuration file
        if args.config_file:
            load_config_file(args.config_file)
        
        # Validate arguments
        validate_args(args)
        
        # Setup logging
        setup_logging(args.log_level, args.log_file)
        
        # Check configuration mode
        if args.check_config:
            print("✅ Configuration check passed")
            print(f"Host: {args.host}:{args.port}")
            print(f"Workers: {args.workers}")
            return
        
        # Print startup information
        print_startup_info(args)
        
        # Start server
        run_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1  # reload mode can only use single process
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        if args.debug if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

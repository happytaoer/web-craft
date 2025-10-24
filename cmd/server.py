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


def setup_logging() -> None:
    """Configure logging system"""
    level = getattr(logging, config.logging.level.upper(), logging.INFO)
    
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


def validate_args(args: argparse.Namespace) -> None:
    """Validate command line arguments"""
    # Validate port range
    if not (1 <= args.port <= 65535):
        raise ValueError(f"Port must be in range 1-65535, current value: {args.port}")
    
    # Validate worker count
    if args.workers < 1:
        raise ValueError(f"Worker count must be greater than 0, current value: {args.workers}")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="🕷️ Web-Craft API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  %(prog)s                                   # Start with default configuration
  %(prog)s --port 8080 --host 0.0.0.0        # Specify port and host
  %(prog)s --reload                          # Development mode with auto-reload
  %(prog)s --workers 4                       # Production mode with 4 worker processes
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
    
    # Other options
    other_group = parser.add_argument_group('Other Options')
    other_group.add_argument(
        '--version', 
        action='version', 
        version='Web-Craft API v1.0.0'
    )
    return parser


def print_startup_info(args: argparse.Namespace) -> None:
    """Print startup information"""
    print("🕷️ Web-Craft API Server")
    print("=" * 50)
    print(f"📡 Host Address: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"👥 Workers: {args.workers}")
    print(f"🔄 Auto Reload: {'Yes' if args.reload else 'No'}")
    print(f"📝 Log Level: {config.logging.level}")
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
        # Validate arguments
        validate_args(args)
        
        # Setup logging
        setup_logging()

        
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Web-Craft - Intelligent Web Scraping System

A Python-based modular web scraping framework focused on efficient single URL crawling, supporting asynchronous processing, API services, and highly customizable spider modules.

## 📸 Screenshot

![Web-Craft Screenshot](screenshot.png)

*Web-Craft API interface and system overview*

## 📦 Quick Installation

### Requirements
- Python 3.7+
- Redis Server 5.0+
- pip package manager

### Installation Steps
```bash
# 1. Clone the project
git clone https://github.com/happytaoer/web-craft.git
cd web-craft

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install and start Redis
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# macOS: brew install redis
redis-server

# 4. Setup configuration
cp config.example.toml config.toml
# Edit config.toml to customize Redis and other settings

# 5. Verify installation
python -m tests.test_ip_crawl
```

## 🏗️ Project Architecture

```
web-craft/
├── input/                  # Input Layer - Parameter Processing
├── worker/                 # Worker Layer - Spider Engine  
├── output/                 # Output Layer - Data Export
├── api/                    # API Layer - Web Interface
│   ├── spider_service.py  # Spider Service (RQ Integration)
│   ├── routes.py          # API Routes
│   └── models.py          # API Data Models
├── cmd/                    # Command Line Tools
│   ├── server.py          # API Server
│   └── crawl.py           # RQ Worker
├── tasks/                  # Task Management System (RQ-based)
│   ├── queue.py           # RQ Task Queue Manager
│   ├── worker_tasks.py    # Worker Task Functions
│   └── models.py          # Task Data Models (legacy)
├── spiders/                # Spider Module System
│   ├── core/              # Framework Core Components
│   │   ├── base_spider.py # Base Spider Abstract Class
│   │   └── spider_loader.py # Spider Loader
│   └── spiders/           # User Custom Spiders
│       ├── default.py     # Default General Spider
│       └── ip.py          # IP Address Spider
├── tests/                  # Test Suite
├── config.py               # Configuration Module
├── config.toml             # Configuration File (user-specific, not in git)
├── config.example.toml     # Configuration Example Template
├── requirements.txt        # Dependencies
└── README.md              # Project Documentation
```

## ✨ Core Features

- 🌐 **RESTful API** - Complete Web API interface
- 🎯 **Single URL Focus** - Efficient single webpage crawling
- ⚡ **RQ Task Queue** - Redis-based distributed task queue with RQ
- 🔧 **Modular Design** - Extensible spider module system
- 🔄 **Auto Retry** - Intelligent retry mechanism and delay control
- 📊 **Job Tracking** - Real-time job status and result tracking
- 🧪 **Custom Parsing** - Users have full control over data extraction logic in parse methods
- 🤖 **AI-Friendly** - Simple interface design makes it perfect for AI-assisted spider development
- 🚀 **Scalable** - Multiple workers can process tasks concurrently

## 🚀 Quick Start

### 1. Start the System

```bash
# Terminal 1: Start Redis server (if not already running)
redis-server

# Terminal 2: Start API server
python cmd/server.py --port 8080

# Terminal 3: Start RQ worker
python cmd/crawl.py

# Optional: Start multiple workers for parallel processing
python cmd/crawl.py  # Worker 2
python cmd/crawl.py  # Worker 3
```

### 2. Use API for Crawling

```bash
# Single URL crawling
curl -X POST "http://127.0.0.1:8080/api/v1/crawl/single" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "spider_name": "default"}'

# Query task status
curl "http://127.0.0.1:8080/api/v1/task/{task_id}/status"

# Get task results
curl "http://127.0.0.1:8080/api/v1/task/{task_id}/result"
```

### 3. Run Tests

```bash
# Verify system functionality
python -m tests.test_ip_crawl
```

## 🔧 Configuration Options

### Configuration File (config.toml)

Web-Craft uses TOML format for configuration management, following Python best practices.

**Setup**: Copy `config.example.toml` to `config.toml` and customize as needed:
```bash
cp config.example.toml config.toml
```

**Note**: `config.toml` is user-specific and should not be committed to version control (add to `.gitignore`).

```toml
[spider]
# Spider configuration
timeout = 30        # Request timeout (seconds)
max_retries = 3     # Maximum retry count
delay = 1.0         # Request delay (seconds)

[redis]
# Redis configuration for RQ task queue
host = "localhost"  # Redis server host
port = 6379         # Redis server port
db = 0              # Redis database number
password = ""       # Redis password (leave empty if no password)
queue_name = "web_craft_tasks"  # RQ queue name

[concurrency]
# Concurrency control configuration
max_concurrent_requests = 10  # Maximum concurrent requests

[server]
# API server configuration
host = "127.0.0.1"
port = 8000
workers = 1

[logging]
# Logging configuration
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Using Configuration in Code

```python
from config import config

# Access configuration
timeout = config.spider.timeout
max_retries = config.spider.max_retries
redis_host = config.redis.host
redis_port = config.redis.port
queue_name = config.redis.queue_name
max_concurrent = config.concurrency.max_concurrent_requests

# Modify configuration at runtime
config.spider.timeout = 60
config.concurrency.max_concurrent_requests = 20
```

### Command Line Arguments

```bash
# API server arguments
python cmd/server.py --port 8080 --host 0.0.0.0
python cmd/server.py --reload --log-level DEBUG
python cmd/server.py --timeout 60 --max-requests 20

# RQ worker arguments
python cmd/crawl.py
python cmd/crawl.py --burst  # Run in burst mode (quit after all jobs processed)
python cmd/crawl.py --queues web_craft_tasks high_priority  # Listen to multiple queues
```
## 📖 API Documentation

After starting the API service, visit the following URLs to view documentation:
- **Swagger UI**: http://127.0.0.1:8080/docs
- **ReDoc**: http://127.0.0.1:8080/redoc

## 🔧 FAQ

### Q: How to create custom spiders?
A: Inherit from BaseSpider class and implement the parse method with full control over data extraction logic:
```python
from spiders.base_spider import BaseSpider
from bs4 import BeautifulSoup

class MySpider(BaseSpider):
    def parse(self, raw_content: str, url: str, headers: dict) -> dict:
        # Use BeautifulSoup or other tools for parsing
        soup = BeautifulSoup(raw_content, 'html.parser')
        
        # Completely custom data extraction logic
        return {
            "title": soup.find('title').get_text() if soup.find('title') else '',
            "headings": [h.get_text() for h in soup.find_all(['h1', 'h2'])],
            "links": [a.get('href') for a in soup.find_all('a', href=True)],
            "custom_field": "your custom extraction logic here"
        }
```

### Q: Why is Web-Craft perfect for AI-assisted development?
A: **Web-Craft's simple and clean interface design makes it ideal for AI code generation:**

🤖 **Minimal Interface Requirements**:
- Only need to implement the `parse()` method in most cases
- Simple method signature: `parse(raw_content: str, url: str, headers: dict) -> dict`
- No complex inheritance chains or framework-specific patterns

🎯 **AI-Friendly Design**:
```python
# AI can easily generate spiders like this:
class AIGeneratedSpider(BaseSpider):
    def parse(self, raw_content: str, url: str, headers: dict) -> dict:
        # AI can focus purely on data extraction logic
        # No need to understand complex framework internals
        soup = BeautifulSoup(raw_content, 'html.parser')
        return {"data": "extracted by AI"}
```

🚀 **Perfect for AI Prompts**:
- "Create a spider that extracts product information from e-commerce pages"
- "Generate a news article spider that gets title, content, and publish date"
- "Build a spider for social media posts with likes, comments, and shares"

The framework handles all the complexity (HTTP requests, retries, async processing, task management) while AI focuses on the core parsing logic!

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📞 Support

If you encounter problems, please:
1. Check the [FAQ](#-faq) section
2. View [API Documentation](#-api-documentation)
3. Run tests to verify system status
4. Submit an Issue describing the problem


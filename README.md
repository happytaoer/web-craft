# Web-Craft - Intelligent Web Scraping System

A Python-based modular web scraping framework focused on efficient single URL crawling, supporting asynchronous processing, API services, and highly customizable spider modules.

## 📸 Screenshot

![Web-Craft Screenshot](screenshot.png)

*Web-Craft API interface and system overview*

## 📦 Quick Installation

### Requirements
- Python 3.7+
- pip package manager

### Installation Steps
```bash
# 1. Clone the project
git clone https://github.com/happytaoer/web-craft.git
cd web-craft

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python -m tests.test_ip_crawl
```

## 🏗️ Project Architecture

```
web-craft/
├── input/                  # Input Layer - Parameter Processing
├── worker/                 # Worker Layer - Spider Engine  
├── output/                 # Output Layer - Data Export
├── api/                    # API Layer - Web Interface
├── cmd/                    # Command Line Tools
│   ├── server.py          # API Server
│   └── crawl.py           # Task Executor
├── tasks/                  # Task Management System
├── spiders/                # Spider Module System
│   ├── base_spider.py     # Base Spider Abstract Class
│   ├── default_spider.py  # Default General Spider
│   └── spider_loader.py   # Spider Loader
├── tests/                  # Test Suite
├── data/                   # Data Storage Directory
│   └── tasks/             # Task File Storage
│       ├── pending/       # Pending Tasks
│       ├── running/       # Running Tasks
│       ├── completed/     # Completed Tasks
│       └── failed/        # Failed Tasks
├── config.py               # Configuration File
├── requirements.txt        # Dependencies
└── README.md              # Project Documentation
```

## ✨ Core Features

- 🌐 **RESTful API** - Complete Web API interface
- 🎯 **Single URL Focus** - Efficient single webpage crawling
- ⚡ **Asynchronous Processing** - Support for async task queues and concurrent processing
- 🔧 **Modular Design** - Extensible spider module system
- 🔄 **Auto Retry** - Intelligent retry mechanism and delay control
- 🧪 **Custom Parsing** - Users have full control over data extraction logic in parse methods
- 🤖 **AI-Friendly** - Simple interface design makes it perfect for AI-assisted spider development

## 🚀 Quick Start

### 1. Start the System

```bash
# Terminal 1: Start API server
python cmd/server.py --port 8080

# Terminal 2: Start task executor
python cmd/crawl.py
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

### Basic Configuration (config.py)

```python
# Request Configuration
DEFAULT_TIMEOUT = 30          # Request timeout (seconds)
DEFAULT_RETRY_COUNT = 3       # Default retry count
DEFAULT_DELAY = 1.0           # Request interval (seconds)

DEFAULT_TASKS_DIR = "data/tasks"      # Task directory

# API Configuration
API_HOST = "127.0.0.1"        # API host
API_PORT = 8000               # API port
```

### Command Line Arguments

```bash
# API server arguments
python cmd/server.py --port 8080 --host 0.0.0.0
python cmd/server.py --reload --log-level DEBUG

# Task executor arguments
python cmd/crawl.py --max-tasks 10 --interval 2
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

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI, asyncio
- **HTTP Client**: aiohttp, requests  
- **Data Processing**: pandas, json
- **Testing Framework**: Custom test suite
- **Deployment**: Supports distributed deployment

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


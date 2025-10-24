"""
FastAPI Application - API Server Main Program
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import uvicorn
import logging
from typing import Dict, Any
from api.routes import router

# Get logger instance (logging is configured in server.py)
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title="Web-Craft API",
    description="""
    **Web-Craft Intelligent Web Scraping System API**
    
    A powerful web scraping API service that supports:
    
    * **Single URL Crawling** - Fast crawling of individual web pages
    * **Custom Data Extraction** - Users have full control over data extraction logic in parse methods
    * **Task Status Tracking** - Real-time monitoring of crawling progress
    * **Console Output** - Crawling results output directly to console
    
    ## Quick Start
    
    1. Use `/crawl/single` to crawl a single web page
    2. Use `/task/{task_id}/status` to query task status
    
    ## Usage Instructions
    
    ### Custom Spiders
    Inherit from BaseSpider class and implement the parse method:
    ```python
    class MySpider(BaseSpider):
        def parse(self, raw_content: str, url: str, headers: dict) -> dict:
            # Completely custom data extraction logic
            soup = BeautifulSoup(raw_content, 'html.parser')
            return {
                "title": soup.find('title').get_text(),
                "custom_data": "your extraction logic"
            }
    ```
    
    ### Request Parameters
    - `url`: Target URL (required)
    - `spider_name`: Spider module name (default: "default")
    - `method`: HTTP request method (default: "GET")
    - `timeout`: Request timeout (default: 30 seconds)
    - `max_retries`: Maximum retry count (default: 3)
    
    The system automatically uses default request header configuration, no manual specification needed.
    """,
    version="1.0.0",
    contact={
        "name": "Web-Craft Team",
        "email": "support@webcraft.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handling"""
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "detail": "Please contact administrator"
        }
    )


# Custom 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc) -> JSONResponse:
    """404 error handling"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "API endpoint not found",
            "error_code": "NOT_FOUND",
            "detail": f"Path {request.url.path} does not exist"
        }
    )


# Include router
app.include_router(router, prefix="/api/v1", tags=["Spider API"])


# Custom OpenAPI documentation
def custom_openapi() -> Dict[str, Any]:
    """Custom OpenAPI documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Web-Craft API",
        version="1.0.0",
        description="Intelligent Web Scraping System API Documentation",
        routes=app.routes,
    )
    
    # Add custom information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", include_in_schema=False)
async def root() -> Dict[str, str]:
    """Root path redirect to documentation"""
    return {
        "message": "🕷️ Web-Craft API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api": "/api/v1"
    }


def run_server(host: str = "0.0.0.0", port: int = 8000, 
               reload: bool = False, workers: int = 1) -> None:
    """Run API server"""
    # Remove duplicate print information, handled uniformly by cmd/server.py
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info"
    )

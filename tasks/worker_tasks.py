"""
Worker Tasks - Functions executed by RQ workers
"""
import asyncio
import time
from typing import Dict, Any
from api.models import SpiderTaskRequest
from spiders.core.spider_loader import spider_loader
from output.data_exporter import DataExporter


def execute_spider_task(
    url: str,
    spider_name: str = "default",
    method: str = "GET",
    timeout: int = 30,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Execute spider crawling task
    
    This function is executed by RQ workers and runs synchronously.
    
    Args:
        url: Target URL
        spider_name: Spider module name
        method: HTTP method
        timeout: Request timeout
        max_retries: Maximum retry count
        
    Returns:
        Task execution result dictionary
    """
    print(f"🚀 Starting spider task")
    print(f"   URL: {url}")
    print(f"   Spider: {spider_name}")
    
    start_time = time.time()
    
    try:
        # Get spider instance
        spider = spider_loader.get_spider(spider_name)
        if not spider:
            raise ValueError(f"Unable to load spider module: {spider_name}")
        
        print(f"   Using spider: {spider.__class__.__name__}")
        
        # Create spider request
        spider_request = SpiderTaskRequest(
            url=url,
            spider_name=spider_name,
            method=method,
            timeout=timeout,
            max_retries=max_retries
        )
        
        # Execute crawling (run async function in sync context)
        result = asyncio.run(spider.crawl_single(spider_request))
        
        execution_time = time.time() - start_time
        
        if result.success:
            print(f"✅ Task completed successfully")
            print(f"   Execution time: {execution_time:.2f} seconds")
            
            # Output results to console
            data_exporter = DataExporter()
            export_data = {
                'url': result.url,
                'status_code': result.status_code,
                'success': result.success,
                'content_length': result.content_length,
                'encoding': result.encoding,
                'headers': result.headers,
                'response_time': result.response_time,
                'extracted_data': result.extracted_data,
                'error_message': result.error_message
            }
            data_exporter.print_result(export_data)
            
            # Return result
            return {
                'success': True,
                'url': result.url,
                'status_code': result.status_code,
                'content_length': result.content_length,
                'encoding': result.encoding,
                'response_time': result.response_time,
                'extracted_data': result.extracted_data,
                'execution_time': execution_time
            }
        else:
            print(f"❌ Task failed: {result.error_message}")
            return {
                'success': False,
                'url': result.url,
                'error_message': result.error_message,
                'execution_time': execution_time
            }
            
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Task execution exception: {str(e)}"
        print(f"❌ {error_msg}")
        
        return {
            'success': False,
            'url': url,
            'error_message': error_msg,
            'execution_time': execution_time
        }

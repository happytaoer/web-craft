"""
Spider task executor
Reads tasks from tasks directory and executes spiders
"""
import argparse
import sys
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tasks.manager import TaskManager
from tasks.models import SpiderTask, TaskStatus, TaskType
from output.data_exporter import DataExporter
from spiders.spider_loader import spider_loader
from api.models import SpiderTaskRequest
from config import Config


class TaskExecutor:
    """Task executor"""
    
    def __init__(self, tasks_dir: str = None):
        """Initialize task executor"""
        if tasks_dir is None:
            tasks_dir = Config.DEFAULT_TASKS_DIR
        self.task_manager = TaskManager(tasks_dir)
        self.data_exporter = DataExporter()
    
    async def execute_task(self, task: SpiderTask) -> bool:
        """
        Execute a single task
        
        Args:
            task: Spider task
            
        Returns:
            Whether execution was successful
        """
        try:
            print(f"🚀 Starting task execution: {task.task_id}")
            print(f"   Spider module: {task.spider_name}")
            print(f"   URL: {task.urls[0] if task.urls else 'N/A'}")
            
            # Get spider instance
            spider = spider_loader.get_spider(task.spider_name)
            if not spider:
                raise ValueError(f"Unable to load spider module: {task.spider_name}")
            
            print(f"   Using spider: {spider.__class__.__name__}")
            
            # Update task status to running
            task.update_status(TaskStatus.RUNNING)
            self.task_manager.update_task(task)
            
            start_time = time.time()
            
            # Currently only supports single URL tasks
            success = await self._execute_single_task(task, spider)
            
            execution_time = time.time() - start_time
            
            if success:
                task.execution_time = execution_time
                task.update_status(TaskStatus.COMPLETED)
                print(f"✅ Task completed: {task.task_id}")
                print(f"   Execution time: {execution_time:.2f} seconds")
                print(f"   Success: {task.successful_count}, Failed: {task.failed_count}")
            else:
                task.update_status(TaskStatus.FAILED, "Task execution failed")
                print(f"❌ Task failed: {task.task_id}")
            
            self.task_manager.update_task(task)
            return success
            
        except Exception as e:
            print(f"❌ Task execution exception: {e}")
            task.update_status(TaskStatus.FAILED, str(e))
            self.task_manager.update_task(task)
            return False
    
    async def _execute_single_task(self, task: SpiderTask, spider) -> bool:
        """Execute single URL task"""
        try:
            url = task.urls[0]
            
            # Create spider request
            spider_request = SpiderTaskRequest(
                url=url,
                spider_name=task.spider_name,
                method=task.method,
                timeout=task.timeout,
                max_retries=task.max_retries,
                delay=task.delay
            )
            
            # Use spider to execute crawling
            result = await spider.crawl_single(spider_request)
            
            if result.success:
                task.successful_count = 1
                task.failed_count = 0
                
                # Output results to console
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
                
                # Output to console
                self.data_exporter.print_result(export_data)
                
                return True
            else:
                task.successful_count = 0
                task.failed_count = 1
                print(f"   Crawling failed: {result.error_message}")
                return False
                
        except Exception as e:
            print(f"❌ Single task execution exception: {e}")
            task.successful_count = 0
            task.failed_count = 1
            return False
    
    async def run_worker(self, max_tasks: Optional[int] = None, interval: float = 5.0):
        """
        Run task worker
        
        Args:
            max_tasks: Maximum number of tasks to process, None means unlimited
            interval: Check interval (seconds)
        """
        print("🕷️ Web-Craft Task Executor Started")
        print(f"   Max tasks: {max_tasks or 'Unlimited'}")
        print(f"   Check interval: {interval} seconds")
        print(f"   Available spiders: {list(spider_loader.list_spiders().keys())}")
        
        processed_count = 0
        
        try:
            while True:
                # Check if maximum task count is reached
                if max_tasks and processed_count >= max_tasks:
                    print(f"✅ Processed {processed_count} tasks, reached maximum limit")
                    break
                
                # Get pending tasks
                pending_tasks = self.task_manager.get_pending_tasks()
                
                if not pending_tasks:
                    print("⏳ No pending tasks, waiting...")
                    await asyncio.sleep(interval)
                    continue
                
                # Process tasks
                for task in pending_tasks:
                    if max_tasks and processed_count >= max_tasks:
                        break
                    
                    try:
                        success = await self.execute_task(task)
                        processed_count += 1
                        
                        if success:
                            print(f"📊 Task statistics: Processed {processed_count} tasks")
                        
                    except Exception as e:
                        print(f"❌ Exception occurred while processing task {task.task_id}: {e}")
                        processed_count += 1
                
                # Brief rest
                await asyncio.sleep(1.0)
                
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal, stopping task executor...")
        except Exception as e:
            print(f"❌ Task executor exception: {e}")
        finally:
            print(f"📊 Task executor stopped, processed {processed_count} tasks in total")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Web-Craft Task Executor")
    parser.add_argument("--tasks-dir", default=Config.DEFAULT_TASKS_DIR, help="Task directory path")
    parser.add_argument("--max-tasks", type=int, help="Maximum number of tasks to process")
    parser.add_argument("--interval", type=float, default=5.0, help="Check interval (seconds)")
    parser.add_argument("--once", action="store_true", help="Process existing tasks only once")
    parser.add_argument("--stats", action="store_true", help="Show task statistics")
    
    args = parser.parse_args()
    
    # Create task executor
    executor = TaskExecutor(args.tasks_dir)
    
    # Show task statistics
    if args.stats:
        print("📊 Task Statistics:")
        pending = executor.task_manager.get_pending_tasks()
        print(f"   Pending tasks: {len(pending)}")
        return
    
    # Run worker
    if args.once:
        # Process existing tasks only once
        asyncio.run(executor.run_worker(args.max_tasks, 0))
    else:
        # Continuously monitor and process tasks
        asyncio.run(executor.run_worker(args.max_tasks, args.interval))


if __name__ == "__main__":
    main()

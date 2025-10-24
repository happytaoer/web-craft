"""
RQ Worker - Processes spider tasks from Redis queue
"""
import argparse
import sys
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rq import Worker, Queue, Connection
from tasks.queue import get_task_queue
from config import config


def start_worker(queue_names=None, burst=False):
    """
    Start RQ worker
    
    Args:
        queue_names: List of queue names to listen to
        burst: If True, worker will quit after processing all jobs
    """
    task_queue = get_task_queue()
    
    if queue_names is None:
        queue_names = [config.redis.queue_name]
    
    print("🕷️ Web-Craft RQ Worker Started")
    print(f"   Redis: {config.redis.host}:{config.redis.port}")
    print(f"   Queues: {queue_names}")
    print(f"   Burst mode: {burst}")
    
    with Connection(task_queue.redis_conn):
        queues = [Queue(name, connection=task_queue.redis_conn) for name in queue_names]
        worker = Worker(queues, connection=task_queue.redis_conn)
        
        try:
            worker.work(burst=burst, with_scheduler=False)
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal, stopping worker...")
        finally:
            print("📊 Worker stopped")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Web-Craft RQ Worker")
    parser.add_argument(
        "--queues", 
        nargs="+", 
        default=None,
        help="Queue names to listen to (default: from config)"
    )
    parser.add_argument(
        "--burst", 
        action="store_true", 
        help="Run in burst mode (quit after all jobs processed)"
    )
    
    args = parser.parse_args()
    
    # Start RQ worker
    start_worker(queue_names=args.queues, burst=args.burst)

if __name__ == "__main__":
    main()

"""
Single URL crawling API test
"""
from .base_test import BaseTest


class SingleCrawlTest(BaseTest):
    """Single URL crawling test class"""
    
    def test_single_crawl_default(self) -> bool:
        """Test default spider single URL crawling"""
        self.print_test_header("Single URL crawl task creation (default spider)", 2)
        
        try:
            data = {
                "url": "https://ip.me",
                "spider_name": "ipspider",
                "timeout": 15,
                "max_retries": 2
            }
            
            response = self.make_request('POST', '/crawl/single', data)
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Single task created successfully")
                self.print_info("API Response", result.get('success', False))
                self.print_info("Message", result.get('message', 'N/A'))

                if result.get('data'):
                    crawl_data = result['data']
                    self.print_info("URL", crawl_data.get('url', 'N/A'))
                    self.print_info("Task ID", crawl_data.get('task_id', 'N/A'))
                    self.print_info("Status Code", crawl_data.get('status_code', 'N/A'))
                    self.print_info("Success", crawl_data.get('success', False))
                return True
            else:
                self.print_error(f"Single task creation failed: HTTP {response.status_code}")
                self.print_info("Response", response.text)
                return False
                
        except Exception as e:
            self.print_error(f"Single task creation exception: {e}")
            return False
    


def test_single_crawl_default():
    """Default spider single crawl test function"""
    tester = SingleCrawlTest()
    return tester.test_single_crawl_default()

if __name__ == "__main__":
    from .base_test import run_test_function, print_test_summary
    
    print("🧪 Single URL Crawling API Test")
    print("=" * 50)
    
    # Check API server
    tester = SingleCrawlTest()
    if not tester.check_api_server():
        print("❌ API server not running, please start the server first:")
        print("   python cmd/server.py --port 8080")
        exit(1)
    
    print("✅ API server running normally")
    
    # Run tests
    tests = [
        (test_single_crawl_default, "Default spider single crawl"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func, test_name in tests:
        if run_test_function(test_func, test_name):
            passed += 1
    
    print_test_summary(passed, total)

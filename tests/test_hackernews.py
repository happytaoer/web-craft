"""
Hacker News spider test
"""
from .base_test import BaseTest


class HackerNewsTest(BaseTest):
    """Hacker News spider test class"""
    
    def test_hackernews_crawl(self) -> bool:
        """Test Hacker News spider crawling"""
        self.print_test_header("Hacker News spider crawl task creation", 2)
        
        try:
            data = {
                "spider_name": "hackernewsspider",
                "timeout": 20
            }
            
            response = self.make_request('POST', '/crawl/single', data)
            
            if response.status_code == 200:
                result = response.json()
                self.print_success("Task created successfully")
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
                self.print_error(f"Task creation failed: HTTP {response.status_code}")
                self.print_info("Response", response.text)
                return False
                
        except Exception as e:
            self.print_error(f"Task creation exception: {e}")
            return False


def test_hackernews_crawl():
    """Hacker News spider test function"""
    tester = HackerNewsTest()
    return tester.test_hackernews_crawl()


if __name__ == "__main__":
    from .base_test import run_test_function, print_test_summary
    
    print("🧪 Hacker News Spider Test")
    print("=" * 50)
    
    # Check API health
    tester = HackerNewsTest()
    if not tester.check_api_server():
        print("\n❌ API server not available, exiting...")
        exit(1)
    
    print("✅ API server running normally")
    
    print()
    
    # Run test
    tests = [
        (test_hackernews_crawl, "Hacker News spider crawl")
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func, test_name in tests:
        if run_test_function(test_func, test_name):
            passed += 1
    
    # Print summary
    print_test_summary(passed, total)

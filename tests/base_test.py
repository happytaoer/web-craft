"""
Base test class - Provides common testing functionality
"""
import requests
import time
from typing import Dict, Any


class BaseTest:
    """Base test class"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> requests.Response:
        """Send HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        if method.upper() == 'GET':
            return self.session.get(url, params=data)
        elif method.upper() == 'POST':
            return self.session.post(url, json=data)
        elif method.upper() == 'PUT':
            return self.session.put(url, json=data)
        elif method.upper() == 'DELETE':
            return self.session.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def check_api_server(self) -> bool:
        """Check if API server is running"""
        try:
            response = self.make_request('GET', '/health')
            return response.status_code == 200
        except Exception:
            return False
    
    def print_test_header(self, title: str, level: int = 1):
        """Print test header"""
        if level == 1:
            print(f"\n{'='*50}")
            print(f"🧪 {title}")
            print(f"{'='*50}")
        elif level == 2:
            print(f"\n{'─'*30}")
            print(f"🔍 {title}")
            print(f"{'─'*30}")
        else:
            print(f"\n• {title}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
    
    def print_info(self, label: str, value: Any):
        """Print information"""
        print(f"   {label}: {value}")


def run_test_function(test_func, test_name: str) -> bool:
    """Run test function"""
    print(f"\n🔍 Running test: {test_name}")
    try:
        result = test_func()
        if result:
            print(f"✅ {test_name} - PASSED")
            return True
        else:
            print(f"❌ {test_name} - FAILED")
            return False
    except Exception as e:
        print(f"❌ {test_name} - ERROR: {e}")
        return False


def print_test_summary(passed: int, total: int):
    """Print test summary"""
    print(f"\n{'='*50}")
    print(f"📊 Test Summary")
    print(f"{'='*50}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Total: {total}")
    
    if passed == total:
        print(f"🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")

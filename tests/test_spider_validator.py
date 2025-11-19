"""
Test Spider Validator
"""
from spiders.core.spider_validator import SpiderValidator


def test_valid_spider():
    """Test validation with valid spider code"""
    valid_code = """
from typing import Dict, Any
from spiders.core.base_spider import BaseSpider


class TestSpider(BaseSpider):
    name = "test"
    start_url = "https://example.com"
    
    def parse(self, raw_content: str, context) -> Dict[str, Any]:
        return {"data": "test"}
"""
    
    result = SpiderValidator.validate_all(valid_code, "test")
    print(f"Valid spider test: {'PASS' if result.success else 'FAIL'}")
    if not result.success:
        for error in result.errors:
            print(f"  - {error.type}: {error.message}")
    return result.success


def test_syntax_error():
    """Test validation with syntax error"""
    invalid_code = """
from typing import Dict, Any
from spiders.core.base_spider import BaseSpider


class TestSpider(BaseSpider):
    name = "test"
    start_url = "https://example.com"
    
    def parse(self, raw_content: str, context) -> Dict[str, Any]  # Missing colon
        return {"data": "test"}
"""
    
    result = SpiderValidator.validate_all(invalid_code, "test")
    print(f"Syntax error test: {'PASS' if not result.success else 'FAIL'}")
    if not result.success:
        for error in result.errors:
            print(f"  - {error.type}: {error.message} (line {error.line})")
    return not result.success


def test_missing_name():
    """Test validation with missing name field"""
    invalid_code = """
from typing import Dict, Any
from spiders.core.base_spider import BaseSpider


class TestSpider(BaseSpider):
    # name field is missing
    start_url = "https://example.com"
    
    def parse(self, raw_content: str, context) -> Dict[str, Any]:
        return {"data": "test"}
"""
    
    result = SpiderValidator.validate_all(invalid_code, "test")
    print(f"Missing name test: {'PASS' if not result.success else 'FAIL'}")
    if not result.success:
        for error in result.errors:
            print(f"  - {error.type}: {error.message}")
    return not result.success


def test_missing_start_url():
    """Test validation with missing start_url field"""
    invalid_code = """
from typing import Dict, Any
from spiders.core.base_spider import BaseSpider


class TestSpider(BaseSpider):
    name = "test"
    # start_url field is missing
    
    def parse(self, raw_content: str, context) -> Dict[str, Any]:
        return {"data": "test"}
"""
    
    result = SpiderValidator.validate_all(invalid_code, "test")
    print(f"Missing start_url test: {'PASS' if not result.success else 'FAIL'}")
    if not result.success:
        for error in result.errors:
            print(f"  - {error.type}: {error.message}")
    return not result.success


def test_missing_parse():
    """Test validation with missing parse method"""
    invalid_code = """
from typing import Dict, Any
from spiders.core.base_spider import BaseSpider


class TestSpider(BaseSpider):
    name = "test"
    start_url = "https://example.com"
    # parse method is missing
"""
    
    result = SpiderValidator.validate_all(invalid_code, "test")
    print(f"Missing parse test: {'PASS' if not result.success else 'FAIL'}")
    if not result.success:
        for error in result.errors:
            print(f"  - {error.type}: {error.message}")
    return not result.success


def test_import_error():
    """Test validation with import error"""
    invalid_code = """
from typing import Dict, Any
from spiders.core.base_spider import BaseSpider
from nonexistent_module import something  # This will cause import error


class TestSpider(BaseSpider):
    name = "test"
    start_url = "https://example.com"
    
    def parse(self, raw_content: str, context) -> Dict[str, Any]:
        return {"data": "test"}
"""
    
    result = SpiderValidator.validate_all(invalid_code, "test")
    print(f"Import error test: {'PASS' if not result.success else 'FAIL'}")
    if not result.success:
        for error in result.errors:
            print(f"  - {error.type}: {error.message}")
    return not result.success


if __name__ == "__main__":
    print("=" * 60)
    print("Spider Validator Tests")
    print("=" * 60)
    
    tests = [
        ("Valid spider", test_valid_spider),
        ("Syntax error", test_syntax_error),
        ("Missing name field", test_missing_name),
        ("Missing start_url field", test_missing_start_url),
        ("Missing parse method", test_missing_parse),
        ("Import error", test_import_error),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    passed = sum(1 for _, p in results if p)
    total = len(results)
    for test_name, passed_flag in results:
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        print(f"{status}: {test_name}")
    print(f"\nTotal: {passed}/{total} tests passed")

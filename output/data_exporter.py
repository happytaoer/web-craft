"""
Output layer - Data output processing module
Responsible for outputting crawl data to the console
"""
import json
from typing import Dict, Any


class DataExporter:
    """Data exporter - Simplified version, only outputs to console"""
    
    def __init__(self):
        """Initialize data exporter"""
        pass
    
    def print_result(self, data: Dict[str, Any]) -> None:
        """
        Print crawl result to console
        
        Args:
            data: Crawl result data
        """
        if not data:
            print("📝 No data to display")
            return
        
        print("📊 Crawl result:")
        print("=" * 50)
        
        # Output basic information
        if 'url' in data:
            print(f"🔗 URL: {data['url']}")
        if 'status_code' in data:
            print(f"📡 Status code: {data['status_code']}")
        if 'success' in data:
            status = "✅ Success" if data['success'] else "❌ Failed"
            print(f"📈 Status: {status}")
        
        # Output extracted data
        if 'extracted_data' in data and data['extracted_data']:
            print("\n🎯 Extracted data:")
            print("-" * 30)
            extracted = data['extracted_data']
            print(json.dumps(extracted, ensure_ascii=False, indent=2))
        
        # Output error message
        if 'error_message' in data and data['error_message']:
            print(f"\n❌ Error message: {data['error_message']}")
        
        print("=" * 50)
"""
Spider Code Validator - Validate user-submitted spider code before saving
"""
import ast
import sys
import importlib
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base_spider import BaseSpider


@dataclass
class ValidationError:
    """Validation error detail"""
    type: str  # syntax_error, import_error, structure_error, field_error
    message: str
    line: Optional[int] = None
    detail: Optional[str] = None


@dataclass
class ValidationResult:
    """Validation result"""
    success: bool
    errors: List[ValidationError]
    
    def add_error(self, error_type: str, message: str, line: Optional[int] = None, detail: Optional[str] = None):
        """Add validation error"""
        self.success = False
        self.errors.append(ValidationError(
            type=error_type,
            message=message,
            line=line,
            detail=detail
        ))


class SpiderValidator:
    """Spider code validator"""
    
    @staticmethod
    def validate_syntax(code: str) -> ValidationResult:
        """
        Step 1: Validate Python syntax using AST
        
        Args:
            code: Spider code string
            
        Returns:
            ValidationResult with syntax errors if any
        """
        result = ValidationResult(success=True, errors=[])
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            result.add_error(
                error_type="syntax_error",
                message=f"Syntax error: {e.msg}",
                line=e.lineno,
                detail=f"at line {e.lineno}, column {e.offset}"
            )
        except Exception as e:
            result.add_error(
                error_type="syntax_error",
                message=f"Failed to parse code: {str(e)}"
            )
        
        return result
    
    @staticmethod
    def validate_import(code: str, spider_name: str) -> ValidationResult:
        """
        Step 2: Test import in temporary isolated environment
        
        Args:
            code: Spider code string
            spider_name: Name for the temporary module
            
        Returns:
            ValidationResult with import errors if any
        """
        result = ValidationResult(success=True, errors=[])
        temp_dir = None
        temp_module_name = None
        
        try:
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix="spider_validation_"))
            
            # Generate unique module name to avoid conflicts
            temp_module_name = f"_test_spider_{uuid.uuid4().hex[:8]}"
            temp_file = temp_dir / f"{temp_module_name}.py"
            
            # Write code to temporary file
            temp_file.write_text(code, encoding='utf-8')
            
            # Add temp directory to sys.path temporarily
            sys.path.insert(0, str(temp_dir))
            
            try:
                # Try to import the module
                module = importlib.import_module(temp_module_name)
                
                # Find spider class
                spider_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseSpider) and 
                        attr != BaseSpider):
                        spider_class = attr
                        break
                
                if spider_class is None:
                    result.add_error(
                        error_type="structure_error",
                        message="No valid spider class found that inherits from BaseSpider"
                    )
                else:
                    # Validate spider structure
                    structure_result = SpiderValidator.validate_structure(spider_class)
                    if not structure_result.success:
                        result.errors.extend(structure_result.errors)
                        result.success = False
                
            except ImportError as e:
                result.add_error(
                    error_type="import_error",
                    message=f"Import error: {str(e)}",
                    detail="Check if all required modules are available"
                )
            except AttributeError as e:
                result.add_error(
                    error_type="import_error",
                    message=f"Attribute error: {str(e)}",
                    detail="Check if all referenced attributes exist"
                )
            except Exception as e:
                result.add_error(
                    error_type="import_error",
                    message=f"Failed to load module: {str(e)}"
                )
            
        finally:
            # Cleanup: remove from sys.path
            if temp_dir and str(temp_dir) in sys.path:
                sys.path.remove(str(temp_dir))
            
            # Cleanup: remove from sys.modules
            if temp_module_name and temp_module_name in sys.modules:
                del sys.modules[temp_module_name]
            
            # Cleanup: delete temporary files
            if temp_dir and temp_dir.exists():
                try:
                    for file in temp_dir.glob("*"):
                        file.unlink()
                    temp_dir.rmdir()
                except Exception:
                    pass  # Best effort cleanup
        
        return result
    
    @staticmethod
    def validate_structure(spider_class) -> ValidationResult:
        """
        Step 3: Validate spider class structure
        
        Args:
            spider_class: Spider class to validate
            
        Returns:
            ValidationResult with structure errors if any
        """
        result = ValidationResult(success=True, errors=[])
        
        # Check if name field exists
        if not hasattr(spider_class, 'name'):
            result.add_error(
                error_type="structure_error",
                message="Spider class must define 'name' field"
            )
        elif spider_class.name is None or not isinstance(spider_class.name, str):
            result.add_error(
                error_type="field_error",
                message="Spider 'name' field must be a non-empty string"
            )
        elif not spider_class.name.strip():
            result.add_error(
                error_type="field_error",
                message="Spider 'name' field cannot be empty"
            )
        
        # Check if start_url field exists
        if not hasattr(spider_class, 'start_url'):
            result.add_error(
                error_type="structure_error",
                message="Spider class must define 'start_url' field"
            )
        elif spider_class.start_url is None or not isinstance(spider_class.start_url, str):
            result.add_error(
                error_type="field_error",
                message="Spider 'start_url' field must be a non-empty string"
            )
        elif not spider_class.start_url.strip():
            result.add_error(
                error_type="field_error",
                message="Spider 'start_url' field cannot be empty"
            )
        
        # Check if parse method exists and is overridden in subclass
        if not hasattr(spider_class, 'parse'):
            result.add_error(
                error_type="structure_error",
                message="Spider class must implement 'parse()' method"
            )
        else:
            # Check if parse is callable
            parse_method = getattr(spider_class, 'parse')
            if not callable(parse_method):
                result.add_error(
                    error_type="structure_error",
                    message="Spider 'parse' must be a callable method"
                )
            # Check if parse method is defined in the spider class itself (not just inherited)
            elif 'parse' not in spider_class.__dict__:
                result.add_error(
                    error_type="structure_error",
                    message="Spider class must override 'parse()' method from BaseSpider"
                )
        
        return result
    
    @staticmethod
    def validate_all(code: str, spider_name: str) -> ValidationResult:
        """
        Run all validation steps
        
        Args:
            code: Spider code string
            spider_name: Spider name for validation
            
        Returns:
            Combined ValidationResult
        """
        # Step 1: Syntax validation
        syntax_result = SpiderValidator.validate_syntax(code)
        if not syntax_result.success:
            return syntax_result
        
        # Step 2: Import and structure validation
        import_result = SpiderValidator.validate_import(code, spider_name)
        
        return import_result

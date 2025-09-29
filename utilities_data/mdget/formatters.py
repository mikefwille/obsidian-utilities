"""
Output formatters for mdget - handles all result formatting and display
"""

import json
from typing import Dict, Any, Optional


def format_output(data: Dict[str, Any], output_format: str, single_property: Optional[str] = None, raw: bool = False):
    """Format property data according to specified format"""
    if not data:
        print("No data found.")
        return
    
    # Handle single property extraction
    if single_property:
        value = data.get(single_property)
        
        if output_format == 'value' or raw:
            if value is None:
                if not raw:
                    print("Property not found")
                return
            
            if isinstance(value, list):
                if raw:
                    for item in value:
                        print(item)
                else:
                    print(', '.join(str(v) for v in value))
            else:
                print(value)
        
        elif output_format == 'json':
            result = {single_property: value}
            print(json.dumps(result, indent=2, default=str))
        
        else:  # keyvalue format (default)
            if value is None:
                print(f"{single_property}: Not found")
            elif isinstance(value, list):
                print(f"{single_property}: {', '.join(str(v) for v in value)}")
            else:
                print(f"{single_property}: {value}")
        
        return
    
    # Handle multiple properties or all properties
    if output_format == 'json':
        print(json.dumps(data, indent=2, default=str))
    
    elif output_format == 'value':
        # For multiple properties in value mode, just print values one per line
        for key, value in data.items():
            if value is not None:
                if isinstance(value, list):
                    if raw:
                        for item in value:
                            print(item)
                    else:
                        print(', '.join(str(v) for v in value))
                else:
                    print(value)
    
    else:  # keyvalue format (default)
        for key, value in data.items():
            if value is None:
                if not raw:
                    print(f"{key}: Not found")
            elif isinstance(value, list):
                if raw:
                    print(f"{key}:")
                    for item in value:
                        print(f"  - {item}")
                else:
                    print(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                print(f"{key}: {value}")


def format_list_value(value):
    """Helper to format list values consistently"""
    if isinstance(value, list):
        return ', '.join(str(v) for v in value)
    return str(value)
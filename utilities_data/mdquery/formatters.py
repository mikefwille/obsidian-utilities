"""
Output formatters for mdquery - handles all result formatting and display
"""

import json
import csv
from typing import Dict, List, Any, Optional


def csv_safe_value(value):
    """Convert value to CSV-safe string, JSON-encoding complex types"""
    return json.dumps(value) if isinstance(value, (list, dict)) else str(value)


def format_output(results: List[Dict[str, Any]], output_format: str, fields: Optional[str] = None, csv_file: str = 'mdquery.csv'):
    """Format search results according to specified format"""
    if not results:
        print("No matching files found.")
        return
    
    if output_format == 'json':
        output_data = []
        for file_data in results:
            if fields:
                field_list = [f.strip() for f in fields.split(',')]
                filtered_data = {
                    'file_path': file_data['relative_path'],
                    'fields': {}
                }
                for field in field_list:
                    filtered_data['fields'][field] = file_data['yaml_data'].get(field, None)
                output_data.append(filtered_data)
            else:
                output_data.append({
                    'file_path': file_data['relative_path'],
                    'yaml_data': file_data['yaml_data']
                })
        print(json.dumps(output_data, indent=2, default=str))
        
    elif output_format == 'table':
        if fields:
            field_list = [f.strip() for f in fields.split(',')]
            # Print header
            print(f"{'File':<40} | {' | '.join(f'{f:<20}' for f in field_list)}")
            print('-' * (42 + sum(22 for _ in field_list)))
            
            # Print rows
            for file_data in results:
                field_values = []
                for field in field_list:
                    if field in file_data['yaml_data']:
                        value = file_data['yaml_data'][field]
                        if isinstance(value, list):
                            value = ', '.join(str(v) for v in value[:3])  # Limit list display
                            if len(file_data['yaml_data'][field]) > 3:
                                value += '...'
                        value = str(value)[:20]  # Truncate long values
                    else:
                        value = 'N/A'
                    field_values.append(f'{value:<20}')
                
                filename = file_data['relative_path'][:40]  # Truncate long paths
                print(f"{filename:<40} | {' | '.join(field_values)}")
        else:
            print("Table format requires --fields option")
    
    elif output_format == 'csv':
        if not fields:
            print("CSV format requires --fields option")
            return
        
        field_list = [f.strip() for f in fields.split(',')]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['file_path'] + field_list)
            
            # Write data rows
            for file_data in results:
                row = [file_data['relative_path']]
                for field in field_list:
                    value = file_data['yaml_data'].get(field, None)
                    row.append(csv_safe_value(value))
                writer.writerow(row)
        
        print(f"CSV exported to {csv_file}")
            
    else:  # list format (default)
        for file_data in results:
            if fields:
                field_list = [f.strip() for f in fields.split(',')]
                field_values = []
                for field in field_list:
                    if field in file_data['yaml_data']:
                        value = file_data['yaml_data'][field]
                        if isinstance(value, list):
                            value = ', '.join(str(v) for v in value)
                        field_values.append(f"{field}: {value}")
                    else:
                        field_values.append(f"{field}: N/A")
                print(f"{file_data['relative_path']} | {' | '.join(field_values)}")
            else:
                print(file_data['relative_path'])
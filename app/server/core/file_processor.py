import json
import pandas as pd
import sqlite3
import io
import re
from typing import Dict, Any, List, Set
from .sql_security import (
    execute_query_safely,
    validate_identifier,
    SQLSecurityError
)
from .constants import NESTED_FIELD_DELIMITER, ARRAY_INDEX_DELIMITER

def sanitize_table_name(table_name: str) -> str:
    """
    Sanitize table name for SQLite by removing/replacing bad characters
    and validating against SQL injection
    """
    # Remove file extension if present
    if '.' in table_name:
        table_name = table_name.rsplit('.', 1)[0]
    
    # Replace bad characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)
    
    # Ensure it starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = '_' + sanitized
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'table'
    
    # Validate the sanitized name
    try:
        validate_identifier(sanitized, "table")
    except SQLSecurityError:
        # If validation fails, use a safe default
        sanitized = f"table_{hash(table_name) % 100000}"
    
    return sanitized

def convert_csv_to_sqlite(csv_content: bytes, table_name: str) -> Dict[str, Any]:
    """
    Convert CSV file content to SQLite table
    """
    try:
        # Sanitize table name
        table_name = sanitize_table_name(table_name)
        
        # Read CSV into pandas DataFrame
        df = pd.read_csv(io.BytesIO(csv_content))
        
        # Clean column names
        df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Connect to SQLite database
        conn = sqlite3.connect("db/database.db")
        
        # Write DataFrame to SQLite
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Get schema information using safe query execution
        cursor_info = execute_query_safely(
            conn,
            "PRAGMA table_info({table})",
            identifier_params={'table': table_name}
        )
        columns_info = cursor_info.fetchall()
        
        schema = {}
        for col in columns_info:
            schema[col[1]] = col[2]  # column_name: data_type
        
        # Get sample data using safe query execution
        cursor_sample = execute_query_safely(
            conn,
            "SELECT * FROM {table} LIMIT 5",
            identifier_params={'table': table_name}
        )
        sample_rows = cursor_sample.fetchall()
        column_names = [col[1] for col in columns_info]
        sample_data = [dict(zip(column_names, row)) for row in sample_rows]
        
        # Get row count using safe query execution
        cursor_count = execute_query_safely(
            conn,
            "SELECT COUNT(*) FROM {table}",
            identifier_params={'table': table_name}
        )
        row_count = cursor_count.fetchone()[0]
        
        conn.close()
        
        return {
            'table_name': table_name,
            'schema': schema,
            'row_count': row_count,
            'sample_data': sample_data
        }
        
    except Exception as e:
        raise Exception(f"Error converting CSV to SQLite: {str(e)}")

def convert_json_to_sqlite(json_content: bytes, table_name: str) -> Dict[str, Any]:
    """
    Convert JSON file content to SQLite table
    """
    try:
        # Sanitize table name
        table_name = sanitize_table_name(table_name)
        
        # Parse JSON
        data = json.loads(json_content.decode('utf-8'))
        
        # Ensure it's a list of objects
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of objects")
        
        if not data:
            raise ValueError("JSON array is empty")
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(data)
        
        # Clean column names
        df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Connect to SQLite database
        conn = sqlite3.connect("db/database.db")
        
        # Write DataFrame to SQLite
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # Get schema information using safe query execution
        cursor_info = execute_query_safely(
            conn,
            "PRAGMA table_info({table})",
            identifier_params={'table': table_name}
        )
        columns_info = cursor_info.fetchall()
        
        schema = {}
        for col in columns_info:
            schema[col[1]] = col[2]  # column_name: data_type
        
        # Get sample data using safe query execution
        cursor_sample = execute_query_safely(
            conn,
            "SELECT * FROM {table} LIMIT 5",
            identifier_params={'table': table_name}
        )
        sample_rows = cursor_sample.fetchall()
        column_names = [col[1] for col in columns_info]
        sample_data = [dict(zip(column_names, row)) for row in sample_rows]
        
        # Get row count using safe query execution
        cursor_count = execute_query_safely(
            conn,
            "SELECT COUNT(*) FROM {table}",
            identifier_params={'table': table_name}
        )
        row_count = cursor_count.fetchone()[0]
        
        conn.close()
        
        return {
            'table_name': table_name,
            'schema': schema,
            'row_count': row_count,
            'sample_data': sample_data
        }
        
    except Exception as e:
        raise Exception(f"Error converting JSON to SQLite: {str(e)}")

def _flatten_record(record: Any, parent_key: str = '', separator: str = NESTED_FIELD_DELIMITER) -> Dict[str, Any]:
    """
    Recursively flatten a nested dictionary or list into a flat dictionary with compound keys.

    Args:
        record: The record to flatten (can be dict, list, or primitive)
        parent_key: The parent key path for nested structures
        separator: Separator for nested field names (default: NESTED_FIELD_DELIMITER)

    Returns:
        A flat dictionary with compound keys for nested structures

    Examples:
        {"user": {"name": "John"}} -> {"user__name": "John"}
        {"tags": ["a", "b"]} -> {"tags_0": "a", "tags_1": "b"}
    """
    items = []

    if isinstance(record, dict):
        for key, value in record.items():
            # Clean the key name
            clean_key = str(key).lower().replace(' ', '_').replace('-', '_')
            new_key = f"{parent_key}{separator}{clean_key}" if parent_key else clean_key

            if isinstance(value, dict):
                # Recursively flatten nested dict
                items.extend(_flatten_record(value, new_key, separator).items())
            elif isinstance(value, list):
                # Expand array items with index notation
                for idx, item in enumerate(value):
                    array_key = f"{new_key}{ARRAY_INDEX_DELIMITER}{idx}"
                    if isinstance(item, (dict, list)):
                        # Recursively flatten nested structures in arrays
                        items.extend(_flatten_record(item, array_key, separator).items())
                    else:
                        items.append((array_key, item))
            else:
                # Primitive value
                items.append((new_key, value))
    elif isinstance(record, list):
        # Handle top-level lists by expanding with indices
        for idx, item in enumerate(record):
            array_key = f"{parent_key}{ARRAY_INDEX_DELIMITER}{idx}" if parent_key else str(idx)
            if isinstance(item, (dict, list)):
                items.extend(_flatten_record(item, array_key, separator).items())
            else:
                items.append((array_key, item))
    else:
        # Primitive value at root
        if parent_key:
            items.append((parent_key, record))
        else:
            items.append(('value', record))

    return dict(items)

def _discover_all_fields(jsonl_content: bytes) -> Set[str]:
    """
    Scan all lines in a JSONL file to discover all possible field names.
    This is necessary because JSONL records may have inconsistent schemas.

    Args:
        jsonl_content: Raw bytes content of the JSONL file

    Returns:
        Set of all discovered field names across all records
    """
    all_fields = set()
    lines = jsonl_content.decode('utf-8').strip().split('\n')

    for line_num, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue

        try:
            record = json.loads(line)
            flattened = _flatten_record(record)
            all_fields.update(flattened.keys())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON on line {line_num}: {str(e)}")

    return all_fields

def convert_jsonl_to_sqlite(jsonl_content: bytes, table_name: str) -> Dict[str, Any]:
    """
    Convert JSONL (JSON Lines) file content to SQLite table.

    JSONL files contain one JSON object per line. This function:
    1. Discovers all possible fields across all records (schema discovery)
    2. Flattens nested objects using NESTED_FIELD_DELIMITER (__)
    3. Expands arrays using ARRAY_INDEX_DELIMITER with indices (_0, _1, etc.)
    4. Creates a SQLite table with all discovered fields
    5. Populates NULL for missing fields in sparse records

    Args:
        jsonl_content: Raw bytes content of the JSONL file
        table_name: Name for the SQLite table

    Returns:
        Dictionary containing table_name, schema, row_count, and sample_data

    Examples:
        Input line: {"user": {"name": "John"}, "tags": ["a", "b"]}
        Output columns: user__name, tags_0, tags_1
    """
    try:
        # Sanitize table name
        table_name = sanitize_table_name(table_name)

        # Decode content
        content = jsonl_content.decode('utf-8').strip()
        if not content:
            raise ValueError("JSONL file is empty")

        # Phase 1: Discover all possible fields
        all_fields = _discover_all_fields(jsonl_content)

        if not all_fields:
            raise ValueError("No fields discovered in JSONL file")

        # Phase 2: Parse all records and flatten them
        lines = content.split('\n')
        records = []

        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                flattened = _flatten_record(record)

                # Ensure all fields are present (fill missing with None)
                complete_record = {field: flattened.get(field, None) for field in all_fields}
                records.append(complete_record)

            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num}: {str(e)}")

        if not records:
            raise ValueError("No valid records found in JSONL file")

        # Convert to pandas DataFrame
        df = pd.DataFrame(records)

        # Clean column names for SQLite compatibility
        df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', str(col)) for col in df.columns]

        # Connect to SQLite database
        conn = sqlite3.connect("db/database.db")

        # Write DataFrame to SQLite
        df.to_sql(table_name, conn, if_exists='replace', index=False)

        # Get schema information using safe query execution
        cursor_info = execute_query_safely(
            conn,
            "PRAGMA table_info({table})",
            identifier_params={'table': table_name}
        )
        columns_info = cursor_info.fetchall()

        schema = {}
        for col in columns_info:
            schema[col[1]] = col[2]  # column_name: data_type

        # Get sample data using safe query execution
        cursor_sample = execute_query_safely(
            conn,
            "SELECT * FROM {table} LIMIT 5",
            identifier_params={'table': table_name}
        )
        sample_rows = cursor_sample.fetchall()
        column_names = [col[1] for col in columns_info]
        sample_data = [dict(zip(column_names, row)) for row in sample_rows]

        # Get row count using safe query execution
        cursor_count = execute_query_safely(
            conn,
            "SELECT COUNT(*) FROM {table}",
            identifier_params={'table': table_name}
        )
        row_count = cursor_count.fetchone()[0]

        conn.close()

        return {
            'table_name': table_name,
            'schema': schema,
            'row_count': row_count,
            'sample_data': sample_data
        }

    except Exception as e:
        raise Exception(f"Error converting JSONL to SQLite: {str(e)}")
import pytest
import json
import pandas as pd
import sqlite3
import os
import io
from pathlib import Path
from unittest.mock import patch
from core.file_processor import convert_csv_to_sqlite, convert_json_to_sqlite, convert_jsonl_to_sqlite


@pytest.fixture
def test_db():
    """Create an in-memory test database"""
    # Create in-memory database
    conn = sqlite3.connect(':memory:')
    
    # Patch the database connection to use our in-memory database
    with patch('core.file_processor.sqlite3.connect') as mock_connect:
        mock_connect.return_value = conn
        yield conn
    
    conn.close()


@pytest.fixture
def test_assets_dir():
    """Get the path to test assets directory"""
    return Path(__file__).parent.parent / "assets"


class TestFileProcessor:
    
    def test_convert_csv_to_sqlite_success(self, test_db, test_assets_dir):
        # Load real CSV file
        csv_file = test_assets_dir / "test_users.csv"
        with open(csv_file, 'rb') as f:
            csv_data = f.read()
        
        table_name = "users"
        result = convert_csv_to_sqlite(csv_data, table_name)
        
        # Verify return structure
        assert result['table_name'] == table_name
        assert 'schema' in result
        assert 'row_count' in result
        assert 'sample_data' in result
        
        # Test the returned data
        assert result['row_count'] == 4  # 4 users in test file
        assert len(result['sample_data']) <= 5  # Should return up to 5 samples
        
        # Verify schema has expected columns (cleaned names)
        assert 'name' in result['schema']
        assert 'age' in result['schema'] 
        assert 'city' in result['schema']
        assert 'email' in result['schema']
        
        # Verify sample data structure and content
        john_data = next((item for item in result['sample_data'] if item['name'] == 'John Doe'), None)
        assert john_data is not None
        assert john_data['age'] == 25
        assert john_data['city'] == 'New York'
        assert john_data['email'] == 'john@example.com'
    
    def test_convert_csv_to_sqlite_column_cleaning(self, test_db, test_assets_dir):
        # Test column name cleaning with real file
        csv_file = test_assets_dir / "column_names.csv"
        with open(csv_file, 'rb') as f:
            csv_data = f.read()
        
        table_name = "test_users"
        result = convert_csv_to_sqlite(csv_data, table_name)
        
        # Verify columns were cleaned in the schema
        assert 'full_name' in result['schema']
        assert 'birth_date' in result['schema']
        assert 'email_address' in result['schema']
        assert 'phone_number' in result['schema']
        
        # Verify sample data has cleaned column names and actual content
        sample = result['sample_data'][0]
        assert 'full_name' in sample
        assert 'birth_date' in sample
        assert 'email_address' in sample
        assert sample['full_name'] == 'John Doe'
        assert sample['birth_date'] == '1990-01-15'
    
    def test_convert_csv_to_sqlite_with_inconsistent_data(self, test_db, test_assets_dir):
        # Test with CSV that has inconsistent row lengths - should raise error
        csv_file = test_assets_dir / "invalid.csv"
        with open(csv_file, 'rb') as f:
            csv_data = f.read()
        
        table_name = "inconsistent_table"
        
        # Pandas will fail on inconsistent CSV data
        with pytest.raises(Exception) as exc_info:
            convert_csv_to_sqlite(csv_data, table_name)
        
        assert "Error converting CSV to SQLite" in str(exc_info.value)
    
    def test_convert_json_to_sqlite_success(self, test_db, test_assets_dir):
        # Load real JSON file
        json_file = test_assets_dir / "test_products.json"
        with open(json_file, 'rb') as f:
            json_data = f.read()
        
        table_name = "products"
        result = convert_json_to_sqlite(json_data, table_name)
        
        # Verify return structure
        assert result['table_name'] == table_name
        assert 'schema' in result
        assert 'row_count' in result
        assert 'sample_data' in result
        
        # Test the returned data
        assert result['row_count'] == 3  # 3 products in test file
        assert len(result['sample_data']) == 3
        
        # Verify schema has expected columns
        assert 'id' in result['schema']
        assert 'name' in result['schema']
        assert 'price' in result['schema']
        assert 'category' in result['schema']
        assert 'in_stock' in result['schema']
        
        # Verify sample data structure and content
        laptop_data = next((item for item in result['sample_data'] if item['name'] == 'Laptop'), None)
        assert laptop_data is not None
        assert laptop_data['price'] == 999.99
        assert laptop_data['category'] == 'Electronics'
        assert laptop_data['in_stock'] == True
    
    def test_convert_json_to_sqlite_invalid_json(self):
        # Test with invalid JSON
        json_data = b'invalid json'
        table_name = "test_table"
        
        with pytest.raises(Exception) as exc_info:
            convert_json_to_sqlite(json_data, table_name)
        
        assert "Error converting JSON to SQLite" in str(exc_info.value)
    
    def test_convert_json_to_sqlite_not_array(self):
        # Test with JSON that's not an array
        json_data = b'{"name": "John", "age": 25}'
        table_name = "test_table"
        
        with pytest.raises(Exception) as exc_info:
            convert_json_to_sqlite(json_data, table_name)
        
        assert "JSON must be an array of objects" in str(exc_info.value)
    
    def test_convert_json_to_sqlite_empty_array(self):
        # Test with empty JSON array
        json_data = b'[]'
        table_name = "test_table"

        with pytest.raises(Exception) as exc_info:
            convert_json_to_sqlite(json_data, table_name)

        assert "JSON array is empty" in str(exc_info.value)


class TestJSONLConversion:

    def test_convert_jsonl_to_sqlite_success(self, test_db, test_assets_dir):
        """Test basic JSONL file conversion with flat structure"""
        jsonl_file = test_assets_dir / "test_events.jsonl"
        with open(jsonl_file, 'rb') as f:
            jsonl_data = f.read()

        table_name = "events"
        result = convert_jsonl_to_sqlite(jsonl_data, table_name)

        # Verify return structure
        assert result['table_name'] == table_name
        assert 'schema' in result
        assert 'row_count' in result
        assert 'sample_data' in result

        # Test the returned data
        assert result['row_count'] == 5  # 5 events in test file
        assert len(result['sample_data']) == 5

        # Verify schema has expected columns
        assert 'event_id' in result['schema']
        assert 'event_type' in result['schema']
        assert 'user_id' in result['schema']
        assert 'page' in result['schema']
        assert 'timestamp' in result['schema']
        assert 'duration' in result['schema']

        # Verify sample data structure and content
        event1 = next((item for item in result['sample_data'] if item['event_id'] == 1), None)
        assert event1 is not None
        assert event1['event_type'] == 'page_view'
        assert event1['user_id'] == 100
        assert event1['page'] == '/home'

    def test_convert_jsonl_nested_objects(self, test_db, test_assets_dir):
        """Test JSONL with nested objects - should flatten with __ delimiter"""
        jsonl_file = test_assets_dir / "test_logs.jsonl"
        with open(jsonl_file, 'rb') as f:
            jsonl_data = f.read()

        table_name = "logs"
        result = convert_jsonl_to_sqlite(jsonl_data, table_name)

        # Verify return structure
        assert result['table_name'] == table_name
        assert result['row_count'] == 5  # 5 log entries

        # Verify nested fields are flattened with __ delimiter
        schema_keys = result['schema'].keys()

        # Check for flattened user fields
        assert any('user__id' in key for key in schema_keys)
        assert any('user__name' in key for key in schema_keys)

        # Check for flattened request fields
        assert any('request__method' in key for key in schema_keys)
        assert any('request__path' in key for key in schema_keys)
        assert any('request__ip' in key for key in schema_keys)

        # Verify data content
        sample = result['sample_data'][0]
        assert sample['timestamp'] == '2024-01-15T10:30:00Z'
        assert sample['level'] == 'INFO'

    def test_convert_jsonl_with_arrays(self, test_db, test_assets_dir):
        """Test JSONL with arrays - should expand with index notation"""
        jsonl_file = test_assets_dir / "test_logs.jsonl"
        with open(jsonl_file, 'rb') as f:
            jsonl_data = f.read()

        table_name = "logs_with_arrays"
        result = convert_jsonl_to_sqlite(jsonl_data, table_name)

        # Verify return structure
        assert result['table_name'] == table_name

        # Verify arrays are expanded with index notation
        schema_keys = result['schema'].keys()

        # Check for array expansion (tags_0, tags_1, tags_2)
        assert any('tags_0' in key for key in schema_keys)
        assert any('tags_1' in key for key in schema_keys)

        # Verify data content from first record has tags: ["auth", "success"]
        sample = result['sample_data'][0]
        assert sample['tags_0'] == 'auth'
        assert sample['tags_1'] == 'success'

    def test_convert_jsonl_inconsistent_schema(self, test_db):
        """Test JSONL with records having different fields"""
        jsonl_data = b'''{"id": 1, "name": "Alice", "age": 30}
{"id": 2, "name": "Bob", "city": "NYC"}
{"id": 3, "age": 25, "email": "charlie@example.com"}'''

        table_name = "inconsistent"
        result = convert_jsonl_to_sqlite(jsonl_data, table_name)

        # Verify all fields from all records are discovered
        assert result['row_count'] == 3
        schema_keys = result['schema'].keys()

        assert 'id' in schema_keys
        assert 'name' in schema_keys
        assert 'age' in schema_keys
        assert 'city' in schema_keys
        assert 'email' in schema_keys

        # Verify NULL values for missing fields
        sample_data = result['sample_data']

        # First record should have age but not city/email
        record1 = next((r for r in sample_data if r['id'] == 1), None)
        assert record1 is not None
        assert record1['name'] == 'Alice'
        assert record1['age'] == 30
        assert record1['city'] is None
        assert record1['email'] is None

        # Second record should have city but not age/email
        record2 = next((r for r in sample_data if r['id'] == 2), None)
        assert record2 is not None
        assert record2['name'] == 'Bob'
        assert record2['age'] is None
        assert record2['city'] == 'NYC'
        assert record2['email'] is None

    def test_convert_jsonl_empty_file(self, test_db):
        """Test handling of empty JSONL file"""
        jsonl_data = b''
        table_name = "empty"

        with pytest.raises(Exception) as exc_info:
            convert_jsonl_to_sqlite(jsonl_data, table_name)

        assert "JSONL file is empty" in str(exc_info.value)

    def test_convert_jsonl_malformed_line(self, test_db):
        """Test handling of malformed JSON line"""
        jsonl_data = b'''{"id": 1, "name": "Alice"}
{this is not valid json}
{"id": 3, "name": "Charlie"}'''

        table_name = "malformed"

        with pytest.raises(Exception) as exc_info:
            convert_jsonl_to_sqlite(jsonl_data, table_name)

        error_msg = str(exc_info.value)
        assert "Invalid JSON on line 2" in error_msg or "Error converting JSONL" in error_msg

    def test_convert_jsonl_column_name_cleaning(self, test_db):
        """Test that special characters in field names are sanitized"""
        jsonl_data = b'''{"user-id": 1, "user name": "Alice", "email@address": "alice@example.com"}
{"user-id": 2, "user name": "Bob", "email@address": "bob@example.com"}'''

        table_name = "special_chars"
        result = convert_jsonl_to_sqlite(jsonl_data, table_name)

        # Verify columns were cleaned (special chars replaced with underscores)
        schema_keys = result['schema'].keys()

        assert 'user_id' in schema_keys
        assert 'user_name' in schema_keys
        assert 'email_address' in schema_keys

        # Verify data integrity after cleaning
        assert result['row_count'] == 2
        sample = result['sample_data'][0]
        assert sample['user_id'] == 1
        assert sample['user_name'] == 'Alice'
        assert sample['email_address'] == 'alice@example.com'
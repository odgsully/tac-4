# Feature: JSONL Support v2

## Feature Description
Add comprehensive support for uploading JSONL (JSON Lines) files to the Natural Language SQL Interface. JSONL files contain one JSON object per line, commonly used for streaming data, logs, and large datasets. The feature will intelligently flatten nested structures, handle arrays, and create a single SQLite table per uploaded JSONL file, matching the existing CSV and JSON upload patterns.

## User Story
As a data analyst
I want to upload JSONL files and query them using natural language
So that I can analyze line-delimited JSON data (logs, streaming data, etc.) without manual conversion

## Problem Statement
Currently, the application only supports CSV and JSON array file uploads. Many data sources export data in JSONL format (newline-delimited JSON), especially for:
- Server logs and application logs
- Large datasets that don't fit in memory as arrays
- Streaming data exports
- Database dumps and backups
- API response collections

Users cannot directly upload and query these JSONL files, forcing them to manually convert the format first.

## Solution Statement
Extend the file processing pipeline to support JSONL files by:
1. Adding a new `convert_jsonl_to_sqlite()` function that reads line-by-line
2. Scanning the entire file to discover all possible fields across all records
3. Flattening nested objects using `__` delimiter (e.g., `user__name`, `metadata__created_at`)
4. Handling nested arrays by using `_0`, `_1` index notation (e.g., `tags_0`, `tags_1`)
5. Storing delimiter constants in a centralized configuration
6. Using only Python standard library (no new dependencies)
7. Updating the UI to indicate JSONL support
8. Creating test JSONL files for validation

## Relevant Files
Use these files to implement the feature:

- **app/server/core/file_processor.py** - Add `convert_jsonl_to_sqlite()` function following the patterns of `convert_csv_to_sqlite()` and `convert_json_to_sqlite()`
  - Implements line-by-line parsing
  - Performs full-file scan for field discovery
  - Handles nested structure flattening

- **app/server/server.py** - Update `/api/upload` endpoint to accept `.jsonl` files
  - Add `.jsonl` to file validation check
  - Route JSONL files to the new conversion function

- **app/server/tests/core/test_file_processor.py** - Add comprehensive test coverage
  - Test basic JSONL conversion
  - Test nested object flattening
  - Test array handling with indices
  - Test edge cases (empty files, malformed lines, missing fields)

- **app/client/src/main.ts** - Update UI text to mention JSONL support
  - Update drop zone text
  - Update file validation

- **app/client/index.html** - Update static text if needed
  - Update modal instructions

- **README.md** - Document JSONL support
  - Update features list
  - Update usage instructions

### New Files

- **app/server/core/constants.py** - Create centralized configuration for delimiters
  - `NESTED_FIELD_DELIMITER = "__"`
  - `ARRAY_INDEX_DELIMITER = "_"`

- **app/server/tests/assets/test_logs.jsonl** - Test file with nested structures and arrays
  - Contains varied log entries with different schemas
  - Includes nested objects and arrays

- **app/server/tests/assets/test_events.jsonl** - Test file with simpler flat structure
  - Contains event data with consistent schema

## Implementation Plan

### Phase 1: Foundation
Create the infrastructure needed to support JSONL processing:
- Add constants file for delimiter configuration
- Research JSONL format handling with Python stdlib
- Study existing file processor patterns for consistency
- Create test JSONL files with various complexity levels

### Phase 2: Core Implementation
Implement the JSONL conversion logic:
- Build `convert_jsonl_to_sqlite()` function with line-by-line parsing
- Implement two-pass processing: discovery pass + conversion pass
- Create field flattening logic for nested objects
- Create array expansion logic with index notation
- Integrate with existing SQLite table creation flow

### Phase 3: Integration
Connect the new functionality to the existing system:
- Update server endpoint validation to accept `.jsonl`
- Update frontend UI text and validation
- Update documentation
- Run comprehensive tests to ensure zero regressions

## Step by Step Tasks

### 1. Create Constants Configuration File
- Create `app/server/core/constants.py`
- Define `NESTED_FIELD_DELIMITER = "__"` for nested object flattening
- Define `ARRAY_INDEX_DELIMITER = "_"` for array indices
- Add docstring explaining delimiter usage and examples

### 2. Create Test JSONL Files
- Create `app/server/tests/assets/test_logs.jsonl` with complex nested structures:
  - Records with nested objects (e.g., `{"user": {"name": "John", "id": 123}}`)
  - Records with arrays (e.g., `{"tags": ["python", "api", "web"]}`)
  - Records with inconsistent schemas (some fields present/missing)
- Create `app/server/tests/assets/test_events.jsonl` with simpler flat structure:
  - Records with consistent flat schema
  - Various data types (strings, numbers, booleans, nulls)

### 3. Implement Core JSONL Conversion Function
- Add `convert_jsonl_to_sqlite()` to `app/server/core/file_processor.py`
- Implement line-by-line JSON parsing using `json.loads()` per line
- Implement discovery pass: scan all lines to collect all possible field paths
- Implement flattening helper function `flatten_record()`:
  - Recursively flatten nested dicts with `__` delimiter
  - Expand arrays to separate columns with index notation (`_0`, `_1`, etc.)
  - Handle edge cases: null values, empty arrays, deep nesting
- Convert flattened records to pandas DataFrame
- Follow existing patterns from `convert_csv_to_sqlite()` and `convert_json_to_sqlite()`
- Use `sanitize_table_name()` and SQL security functions
- Return schema, row count, and sample data in same format as other converters

### 4. Add Unit Tests for JSONL Conversion
- Add test class `TestJSONLConversion` to `app/server/tests/core/test_file_processor.py`
- Test: `test_convert_jsonl_to_sqlite_success()` - Basic JSONL file conversion
- Test: `test_convert_jsonl_nested_objects()` - Nested object flattening with `__`
- Test: `test_convert_jsonl_with_arrays()` - Array handling with index notation
- Test: `test_convert_jsonl_inconsistent_schema()` - Records with different fields
- Test: `test_convert_jsonl_empty_file()` - Empty JSONL file handling
- Test: `test_convert_jsonl_malformed_line()` - Invalid JSON line handling
- Test: `test_convert_jsonl_column_name_cleaning()` - Special character sanitization

### 5. Update Server Endpoint
- Edit `app/server/server.py` in the `/api/upload` endpoint
- Update file validation check from `('.csv', '.json')` to `('.csv', '.json', '.jsonl')`
- Add conditional routing for `.jsonl` files to call `convert_jsonl_to_sqlite()`
- Ensure error handling covers JSONL-specific errors
- Test endpoint manually to ensure proper routing

### 6. Update Frontend File Upload UI
- Edit `app/client/src/main.ts` in `handleFileUpload()` function
- Update accepted file types to include `.jsonl`
- Update any client-side validation messages
- Edit drop zone text to mention JSONL support (look for text like "drag and drop .csv or .json files")

### 7. Update Frontend UI Text
- Edit `app/client/index.html`
- Find the upload modal section
- Update instructional text to include JSONL format
- Update any tooltip or help text that mentions supported formats

### 8. Update Documentation
- Edit `README.md`
- Update "Features" section to list JSONL support
- Update "Usage" section to mention `.jsonl` files
- Add example of JSONL format in documentation
- Update API Endpoints section to reflect `.jsonl` support in `/api/upload`

### 9. Run Full Test Suite
- Execute `cd app/server && uv run pytest` to run all server tests
- Verify all new JSONL tests pass
- Verify existing CSV and JSON tests still pass (zero regressions)
- Review test coverage for the new functionality

### 10. Manual End-to-End Testing
- Start the application using `./scripts/start.sh`
- Upload `test_logs.jsonl` via the UI
- Verify table is created with flattened columns
- Query the uploaded data using natural language
- Verify results are correctly displayed
- Upload `test_events.jsonl` and repeat validation
- Test uploading JSONL with same name (should replace existing table)
- Test error handling with invalid JSONL file

### 11. Validation and Regression Testing
- Run complete validation using all commands from "Validation Commands" section
- Execute server tests with verbose output
- Start application and test all file formats (CSV, JSON, JSONL)
- Verify no regressions in existing functionality
- Document any issues discovered and resolve them

## Testing Strategy

### Unit Tests
- **JSONL parsing**: Test line-by-line JSON parsing handles valid and invalid lines
- **Field discovery**: Test discovery pass correctly identifies all fields across all records
- **Nested flattening**: Test nested objects are flattened with `__` delimiter correctly
- **Array expansion**: Test arrays are converted to indexed columns (`_0`, `_1`, etc.)
- **Schema consistency**: Test handling of records with different fields (sparse data)
- **Edge cases**: Test empty files, single-line files, malformed JSON lines
- **Column naming**: Test special characters in field names are sanitized
- **Type handling**: Test various JSON types (string, number, boolean, null, nested)

### Integration Tests
- **Upload endpoint**: Test `/api/upload` accepts and processes JSONL files
- **Table creation**: Test SQLite tables are created correctly from JSONL
- **Schema retrieval**: Test `/api/schema` returns correct schema for JSONL-derived tables
- **Query execution**: Test natural language queries work on JSONL-derived tables
- **File replacement**: Test uploading JSONL with same name replaces existing table

### Edge Cases
- **Empty JSONL file**: Should fail gracefully with clear error message
- **Malformed JSON line**: Should identify line number and report error
- **Deeply nested objects**: Test 3+ levels of nesting are handled correctly
- **Large arrays**: Test arrays with 10+ items are expanded correctly
- **Missing fields**: Test records with missing fields populate NULL values
- **Duplicate field names**: Test collision handling when flattened names collide
- **Very long field names**: Test field names are truncated/sanitized if too long
- **Special characters in keys**: Test Unicode, spaces, special chars in JSON keys
- **Mixed types**: Test same field with different types across records
- **Large files**: Test performance with JSONL files containing 10,000+ lines

## Acceptance Criteria
1. Users can successfully upload `.jsonl` files through the drag-and-drop interface
2. JSONL files are parsed line-by-line without loading entire file into memory
3. All unique fields across all records are discovered and included in the schema
4. Nested objects are flattened using `__` delimiter (e.g., `metadata__user__id`)
5. Arrays are expanded to indexed columns using `_` notation (e.g., `tags_0`, `tags_1`)
6. Delimiter constants are stored in `app/server/core/constants.py` and are configurable
7. No new external dependencies are added (uses only Python stdlib)
8. UI clearly indicates JSONL files are supported
9. Test JSONL files exist in `app/server/tests/assets/` directory
10. All unit tests pass with 100% success rate
11. Existing CSV and JSON upload functionality has zero regressions
12. Documentation is updated to reflect JSONL support
13. Error messages for JSONL parsing are clear and actionable
14. JSONL-derived tables can be queried using natural language like other tables
15. Tables created from JSONL can be deleted via the UI

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/server && uv run pytest tests/core/test_file_processor.py -v` - Run file processor tests with verbose output
- `cd app/server && uv run pytest tests/core/test_file_processor.py::TestJSONLConversion -v` - Run only JSONL tests
- `./scripts/start.sh` - Start the application to manually test JSONL upload end-to-end
- `cd app/server && uv run python -c "from core.constants import NESTED_FIELD_DELIMITER, ARRAY_INDEX_DELIMITER; print(f'Delimiters: {NESTED_FIELD_DELIMITER}, {ARRAY_INDEX_DELIMITER}')"` - Verify constants are accessible

## Notes

### Implementation Considerations
- **Memory efficiency**: Use line-by-line processing for large JSONL files instead of loading entire file
- **Two-pass approach**: First pass discovers all possible fields, second pass processes and fills data
- **NULL handling**: Records missing certain fields should populate NULL values for those columns
- **Performance**: For very large JSONL files (millions of lines), consider sampling strategy for field discovery
- **Array expansion limit**: Consider limiting array expansion to prevent table with thousands of columns (e.g., max 100 items)

### Future Enhancements (Not in scope for v2)
- Streaming upload for very large JSONL files (>1GB)
- Configurable array handling (expand vs. JSON string storage)
- Configurable nested depth limit
- Type inference and conversion (e.g., detect date strings and convert to SQLite dates)
- Compressed JSONL support (.jsonl.gz)
- Progress indicator for large file uploads

### Security Considerations
- Reuse existing `sanitize_table_name()` function to prevent SQL injection
- Validate each JSON line independently to prevent malformed data from corrupting entire import
- Use existing `validate_identifier()` for generated column names from nested/array fields
- Follow existing security patterns from `sql_security.py`

### Delimiter Examples
```python
# Nested object example
Input:  {"user": {"profile": {"name": "John"}}}
Output: Column name: "user__profile__name"

# Array example
Input:  {"tags": ["python", "api", "web"]}
Output: Column names: "tags_0", "tags_1", "tags_2"

# Combined example
Input:  {"metadata": {"authors": [{"name": "Alice"}, {"name": "Bob"}]}}
Output: Column names: "metadata__authors_0__name", "metadata__authors_1__name"
```

### Test Data Examples
The test JSONL files should include:
- **test_logs.jsonl**: Server logs with nested request/response objects, variable fields
- **test_events.jsonl**: User events with consistent flat schema, all fields present

This ensures comprehensive testing of both complex and simple JSONL structures.

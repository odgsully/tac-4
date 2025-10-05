"""
Configuration constants for the Natural Language SQL Interface.

This module contains centralized configuration values used across the application,
particularly for data processing and transformation operations.
"""

# Delimiters for flattening nested JSON structures
# Used when converting nested objects and arrays to flat database columns

# NESTED_FIELD_DELIMITER: Used to flatten nested object keys
# Example: {"user": {"profile": {"name": "John"}}} -> "user__profile__name"
NESTED_FIELD_DELIMITER = "__"

# ARRAY_INDEX_DELIMITER: Used to expand array items into separate columns
# Example: {"tags": ["python", "api", "web"]} -> "tags_0", "tags_1", "tags_2"
ARRAY_INDEX_DELIMITER = "_"

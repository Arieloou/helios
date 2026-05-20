"""
pytest configuration and shared fixtures for the encryption_service test suite.

conftest.py is automatically loaded by pytest before any test module.
"""

import sys
import os

# Ensure the encryption_service root is on sys.path so that
# 'app.xxx' imports resolve correctly when running pytest from
# the encryption_service directory.
_service_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _service_root not in sys.path:
    sys.path.insert(0, _service_root)

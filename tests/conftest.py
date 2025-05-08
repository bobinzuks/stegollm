"""
Pytest configuration file for StegoLLM tests.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_config():
    """
    Return a sample configuration for testing.
    """
    return {
        "compression": {
            "enabled": True,
            "strategy": "dictionary",
            "deep_learning_enabled": False,
        },
        "security": {
            "tls_termination": True,
            "clean_sensitive_data": True,
        },
        "metrics": {
            "enabled": True,
            "log_level": "info",
        },
        "api_compat": {
            "enabled": True,
            "supported_apis": ["openai", "claude", "gemini"],
        },
        "custom_instructions": {
            "enabled": True,
            "path": None,
        },
        "ui": {
            "theme": "dark",
        },
    }

@pytest.fixture
def sample_prompts():
    """
    Return sample prompts for testing.
    """
    return [
        "Write a function to implement quicksort in Python",
        "Explain how to optimize database queries for better performance",
        "Create a class for handling authentication in a web application",
        "What is the difference between a binary tree and a binary search tree?",
        "How do I implement a RESTful API in Node.js?",
    ]

@pytest.fixture
def sample_custom_instructions():
    """
    Return sample custom instructions for testing.
    """
    return {
        "rules": [
            {"pattern": "test pattern", "replacement": "TP:"},
            {"pattern": "another test", "replacement": "AT:"},
        ],
        "dictionaries": [
            {
                "name": "test_dict",
                "entries": {
                    "test entry": "TE",
                    "another entry": "AE",
                }
            }
        ]
    }
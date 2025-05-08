"""
Tests for the dictionary-based compression strategy.
"""

import pytest
from stegollm.strategies.dictionary import DictionaryStrategy

def test_compression_decompression():
    """Test that compression and decompression work correctly."""
    config = {
        "compression": {
            "enabled": True,
            "strategy": "dictionary",
        }
    }
    
    strategy = DictionaryStrategy(config)
    
    # Test cases
    test_cases = [
        "Write a function to calculate fibonacci numbers",
        "Explain how to implement a binary search tree in Python",
        "What is the difference between an array and a linked list?",
        "Create a class for managing database connections in JavaScript",
        "How do I optimize the performance of my application?",
    ]
    
    for original in test_cases:
        # Compress
        compressed = strategy.compress(original)
        
        # Verify compression actually happened
        assert len(compressed) < len(original), f"Compression failed for: {original}"
        
        # Decompress
        decompressed = strategy.decompress(compressed)
        
        # Verify we get back the original
        assert decompressed == original, f"Decompression failed for: {original}"

def test_compression_ratio():
    """Test the compression ratio for common prompts."""
    config = {
        "compression": {
            "enabled": True,
            "strategy": "dictionary",
        }
    }
    
    strategy = DictionaryStrategy(config)
    
    # Test prompts with expected minimum compression ratio
    test_prompts = [
        (
            "Write a function to implement quicksort in Python with detailed comments",
            0.20,  # Expect at least 20% compression
        ),
        (
            "Explain how to optimize database queries for better performance in a production environment",
            0.25,  # Expect at least 25% compression
        ),
        (
            "Create a class for handling authentication in a web application using TypeScript and React",
            0.30,  # Expect at least 30% compression
        ),
    ]
    
    for original, min_ratio in test_prompts:
        # Compress
        compressed = strategy.compress(original)
        
        # Calculate compression ratio
        original_len = len(original)
        compressed_len = len(compressed)
        saved_chars = original_len - compressed_len
        ratio = saved_chars / original_len
        
        # Verify the compression ratio
        assert ratio >= min_ratio, f"Compression ratio for '{original}' was {ratio:.2f}, expected at least {min_ratio:.2f}"
        
        # Print the compression stats
        print(f"Original: {original_len} chars, Compressed: {compressed_len} chars")
        print(f"Saved: {saved_chars} chars ({ratio:.2%})")
        print(f"Original: '{original}'")
        print(f"Compressed: '{compressed}'")
        print()

def test_word_boundary_handling():
    """Test that the strategy correctly handles word boundaries."""
    config = {
        "compression": {
            "enabled": True,
            "strategy": "dictionary",
        }
    }
    
    strategy = DictionaryStrategy(config)
    
    # Test cases where we don't want partial matches
    # For example, "class" should not be replaced in "subclass"
    test_cases = [
        ("subclass", "subclass"),  # Should not change
        ("classification", "classification"),  # Should not change
        ("functional", "functional"),  # Should not be affected by "function" replacement
        ("methodology", "methodology"),  # Should not be affected by "method" replacement
    ]
    
    for original, expected in test_cases:
        compressed = strategy.compress(original)
        assert compressed == expected, f"Word boundary handling failed for: {original}, got: {compressed}, expected: {expected}"

def test_custom_dictionaries():
    """Test that custom dictionaries are applied correctly."""
    import tempfile
    import json
    import os
    
    # Create a temporary custom dictionary file
    custom_dict = {
        "rules": [
            {"pattern": "custom pattern", "replacement": "CP:"},
            {"pattern": "another custom", "replacement": "AC:"},
        ],
        "dictionaries": [
            {
                "name": "test_dict",
                "entries": {
                    "custom entry": "CE",
                    "another entry": "AE",
                }
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(custom_dict, f)
        custom_path = f.name
    
    try:
        # Create strategy with custom dictionary
        config = {
            "compression": {
                "enabled": True,
                "strategy": "dictionary",
            },
            "custom_instructions": {
                "path": custom_path,
            }
        }
        
        strategy = DictionaryStrategy(config)
        
        # Test custom patterns
        test_cases = [
            ("This is a custom pattern test", "This is a CP: test"),
            ("Here is another custom test", "Here is AC: test"),
            ("This contains a custom entry here", "This contains a CE here"),
            ("And another entry as well", "And AE as well"),
        ]
        
        for original, expected in test_cases:
            compressed = strategy.compress(original)
            assert compressed == expected, f"Custom dictionary test failed for: {original}, got: {compressed}, expected: {expected}"
    
    finally:
        # Clean up the temporary file
        os.unlink(custom_path)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
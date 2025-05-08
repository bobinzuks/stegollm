"""
Tests for the steganography engine.
"""

import pytest
from stegollm.core.stego_engine import StegoEngine
from stegollm.strategies.dictionary import DictionaryStrategy

def test_stego_engine_initialization(sample_config):
    """Test that the StegoEngine initializes correctly."""
    engine = StegoEngine(sample_config)
    
    # Check that the engine loaded the correct strategy
    assert engine.strategy_name == "dictionary"
    assert isinstance(engine.strategy, DictionaryStrategy)
    
    # Check that deep learning is disabled
    assert engine.deep_learning_enabled is False
    assert engine.deep_learning_strategy is None

def test_compression_decompression(sample_config, sample_prompts):
    """Test that compression and decompression work correctly through the engine."""
    engine = StegoEngine(sample_config)
    
    for original in sample_prompts:
        # Compress
        compressed = engine.compress(original)
        
        # Verify compression actually happened
        assert len(compressed) < len(original), f"Compression failed for: {original}"
        
        # Decompress
        decompressed = engine.decompress(compressed)
        
        # Verify we get back the original
        assert decompressed == original, f"Decompression failed for: {original}"

def test_strategy_switching(sample_config):
    """Test that switching strategies works correctly."""
    engine = StegoEngine(sample_config)
    
    # Initial strategy should be dictionary
    assert engine.strategy_name == "dictionary"
    assert isinstance(engine.strategy, DictionaryStrategy)
    
    # Try to switch to an invalid strategy
    # This should fall back to dictionary
    engine.set_strategy("invalid_strategy")
    assert engine.strategy_name == "invalid_strategy"  # Name is updated
    assert isinstance(engine.strategy, DictionaryStrategy)  # But still using DictionaryStrategy
    
    # Switch back to dictionary
    engine.set_strategy("dictionary")
    assert engine.strategy_name == "dictionary"
    assert isinstance(engine.strategy, DictionaryStrategy)

def test_deep_learning_toggle(sample_config):
    """Test toggling deep learning compression."""
    # Start with deep learning disabled
    config = sample_config.copy()
    engine = StegoEngine(config)
    
    assert engine.deep_learning_enabled is False
    assert engine.deep_learning_strategy is None
    
    # Try to enable deep learning
    # This will fail because we don't have a deep_learning strategy implemented
    # and should gracefully handle the error
    engine.toggle_deep_learning(True)
    
    # Deep learning should still be disabled due to missing implementation
    assert engine.deep_learning_enabled is False
    assert engine.deep_learning_strategy is None
    
    # Turn it off explicitly
    engine.toggle_deep_learning(False)
    assert engine.deep_learning_enabled is False
    assert engine.deep_learning_strategy is None

def test_compression_error_handling(sample_config):
    """Test that compression errors are handled gracefully."""
    engine = StegoEngine(sample_config)
    
    # Create a mock strategy that raises an exception
    class MockStrategy:
        def __init__(self, *args, **kwargs):
            pass
        
        def compress(self, *args, **kwargs):
            raise ValueError("Mock compression error")
        
        def decompress(self, *args, **kwargs):
            raise ValueError("Mock decompression error")
    
    # Replace the engine's strategy with our mock
    engine.strategy = MockStrategy()
    
    # Compression should return the original prompt on error
    original = "Test prompt"
    compressed = engine.compress(original)
    assert compressed == original
    
    # Decompression should return the original compressed prompt on error
    compressed = "Compressed prompt"
    decompressed = engine.decompress(compressed)
    assert decompressed == compressed

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
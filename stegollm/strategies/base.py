"""
Base compression strategy for StegoLLM.

This module contains the BaseStrategy abstract class that all compression
strategies must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseStrategy(ABC):
    """
    Base class for compression strategies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
    
    @abstractmethod
    def compress(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Compress a prompt.
        
        Args:
            prompt: The prompt to compress.
            context: Optional context information to aid compression.
            
        Returns:
            The compressed prompt.
        """
        pass
    
    @abstractmethod
    def decompress(self, compressed_prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Decompress a compressed prompt.
        
        Args:
            compressed_prompt: The compressed prompt to decompress.
            context: Optional context information to aid decompression.
            
        Returns:
            The decompressed prompt.
        """
        pass
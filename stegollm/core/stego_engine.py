"""
Steganography engine for StegoLLM.

This module contains the StegoEngine class that compresses and decompresses
LLM prompts using various compression strategies.
"""

import importlib
from typing import Dict, Any, Optional, List, Type, Union

from stegollm.utils.logging import setup_logger
from stegollm.strategies.base import BaseStrategy

# Setup logger
logger = setup_logger(__name__)

class StegoEngine:
    """
    Steganography engine for compressing and decompressing LLM prompts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the engine.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.strategy_name = config["compression"]["strategy"]
        self.strategy = self._load_strategy(self.strategy_name)
        
        # Deep learning toggle
        self.deep_learning_enabled = config["compression"]["deep_learning_enabled"]
        self.deep_learning_strategy = None
        
        if self.deep_learning_enabled:
            try:
                self.deep_learning_strategy = self._load_strategy("deep_learning")
                logger.info("Deep learning compression enabled.")
            except Exception as e:
                logger.error(f"Could not load deep learning strategy: {str(e)}")
                self.deep_learning_enabled = False
    
    def _load_strategy(self, strategy_name: str) -> BaseStrategy:
        """
        Load a compression strategy.
        
        Args:
            strategy_name: Name of the strategy to load.
            
        Returns:
            Strategy instance.
            
        Raises:
            ImportError: If the strategy could not be loaded.
        """
        try:
            # Import the strategy module
            module_name = f"stegollm.strategies.{strategy_name}"
            module = importlib.import_module(module_name)
            
            # Get the strategy class
            class_name = "".join(word.capitalize() for word in strategy_name.split("_")) + "Strategy"
            strategy_class = getattr(module, class_name)
            
            # Instantiate the strategy
            strategy = strategy_class(self.config)
            logger.info(f"Loaded compression strategy: {strategy_name}")
            
            return strategy
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not load strategy '{strategy_name}': {str(e)}")
            logger.info("Falling back to dictionary strategy.")
            
            # Fall back to dictionary strategy
            from stegollm.strategies.dictionary import DictionaryStrategy
            return DictionaryStrategy(self.config)
    
    def set_strategy(self, strategy_name: str) -> None:
        """
        Set the active compression strategy.
        
        Args:
            strategy_name: Name of the strategy to set.
        """
        self.strategy_name = strategy_name
        self.strategy = self._load_strategy(strategy_name)
        self.config["compression"]["strategy"] = strategy_name
        logger.info(f"Changed compression strategy to: {strategy_name}")
    
    def toggle_deep_learning(self, enabled: bool) -> None:
        """
        Toggle deep learning compression.
        
        Args:
            enabled: Whether to enable deep learning compression.
        """
        self.deep_learning_enabled = enabled
        self.config["compression"]["deep_learning_enabled"] = enabled
        
        if enabled and not self.deep_learning_strategy:
            try:
                self.deep_learning_strategy = self._load_strategy("deep_learning")
                logger.info("Deep learning compression enabled.")
            except Exception as e:
                logger.error(f"Could not load deep learning strategy: {str(e)}")
                self.deep_learning_enabled = False
                self.config["compression"]["deep_learning_enabled"] = False
        
        logger.info(f"Deep learning compression {'enabled' if enabled else 'disabled'}.")
    
    def compress(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Compress a prompt using the active strategy.
        
        Args:
            prompt: The prompt to compress.
            context: Optional context information to aid compression.
            
        Returns:
            The compressed prompt.
        """
        try:
            # Apply deep learning compression first if enabled
            if self.deep_learning_enabled and self.deep_learning_strategy:
                logger.debug("Applying deep learning compression.")
                prompt = self.deep_learning_strategy.compress(prompt, context)
            
            # Apply the main strategy
            logger.debug(f"Applying {self.strategy_name} compression.")
            compressed = self.strategy.compress(prompt, context)
            
            return compressed
        except Exception as e:
            logger.error(f"Error compressing prompt: {str(e)}")
            # Return the original prompt if compression fails
            return prompt
    
    def decompress(self, compressed_prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Decompress a compressed prompt.
        
        Args:
            compressed_prompt: The compressed prompt to decompress.
            context: Optional context information to aid decompression.
            
        Returns:
            The decompressed prompt.
        """
        try:
            # Apply the main strategy
            logger.debug(f"Applying {self.strategy_name} decompression.")
            decompressed = self.strategy.decompress(compressed_prompt, context)
            
            # Apply deep learning decompression if enabled
            if self.deep_learning_enabled and self.deep_learning_strategy:
                logger.debug("Applying deep learning decompression.")
                decompressed = self.deep_learning_strategy.decompress(decompressed, context)
            
            return decompressed
        except Exception as e:
            logger.error(f"Error decompressing prompt: {str(e)}")
            # Return the original prompt if decompression fails
            return compressed_prompt
    
    def transform_response(self, response: str) -> str:
        """
        Transform an LLM response.
        
        In most cases, no transformation is needed for the response,
        but we might need to transform it in some way.
        
        Args:
            response: The response to transform.
            
        Returns:
            The transformed response.
        """
        # Currently, we don't need to transform responses
        return response
"""
Dictionary-based compression strategy for StegoLLM.

This module contains the DictionaryStrategy class that compresses and decompresses
LLM prompts using a dictionary-based approach, replacing common phrases with shorter symbols.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from stegollm.strategies.base import BaseStrategy
from stegollm.utils.logging import setup_logger

# Setup logger
logger = setup_logger(__name__)

class DictionaryStrategy(BaseStrategy):
    """
    Dictionary-based compression strategy.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the strategy.
        
        Args:
            config: Configuration dictionary.
        """
        super().__init__(config)
        
        # Load default dictionaries
        self.compression_dict, self.decompression_dict = self._load_dictionaries()
        
        # Load custom dictionaries if specified
        custom_path = config.get("custom_instructions", {}).get("path")
        if custom_path:
            self._load_custom_dictionaries(custom_path)
    
    def _load_dictionaries(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Load the default compression dictionaries.
        
        Returns:
            Tuple of compression and decompression dictionaries.
        """
        # Default dictionaries for common programming and LLM prompts
        compression_dict = {
            # Programming instructions
            "Write a function": "WF:",
            "Implement a function": "IF:",
            "Create a class": "CC:",
            "Design a": "D:",
            "Explain how": "EH:",
            "What is": "WI:",
            "How do I": "HDI:",
            
            # Programming languages
            "Python": "PY",
            "JavaScript": "JS",
            "TypeScript": "TS",
            "Java": "JV",
            "C++": "CPP",
            "C#": "CS",
            "Go": "GO",
            "Rust": "RS",
            
            # Common concepts
            "algorithm": "algo",
            "function": "fn",
            "variable": "var",
            "class": "cls",
            "object": "obj",
            "method": "mth",
            "interface": "iface",
            "implementation": "impl",
            "database": "db",
            "asynchronous": "async",
            "synchronous": "sync",
            "framework": "fwk",
            "library": "lib",
            "utility": "util",
            "directory": "dir",
            "repository": "repo",
            "configuration": "cfg",
            "development": "dev",
            "production": "prod",
            "environment": "env",
            "application": "app",
            "optimization": "opt",
            "performance": "perf",
            "documentation": "docs",
            "attribute": "attr",
            "parameter": "param",
            "argument": "arg",
            
            # LLM-specific
            "Summarize": "SUM:",
            "Translate": "TR:",
            "Compare": "CMP:",
            "Analyze": "ANL:",
            "Critique": "CRT:",
            "Evaluate": "EVAL:",
            "Generate": "GEN:",
        }
        
        # Create decompression dictionary by swapping keys and values
        decompression_dict = {v: k for k, v in compression_dict.items()}
        
        return compression_dict, decompression_dict
    
    def _load_custom_dictionaries(self, path: str) -> None:
        """
        Load custom dictionaries from a JSON file.
        
        Args:
            path: Path to the JSON file.
        """
        try:
            file_path = Path(path)
            if not file_path.exists():
                logger.warning(f"Custom dictionary file not found: {path}")
                return
            
            with open(file_path, "r") as f:
                custom_data = json.load(f)
            
            # Load custom rules
            if "rules" in custom_data:
                for rule in custom_data["rules"]:
                    pattern = rule.get("pattern")
                    replacement = rule.get("replacement")
                    if pattern and replacement:
                        self.compression_dict[pattern] = replacement
                        self.decompression_dict[replacement] = pattern
            
            # Load custom dictionaries
            if "dictionaries" in custom_data:
                for dictionary in custom_data["dictionaries"]:
                    entries = dictionary.get("entries", {})
                    for key, value in entries.items():
                        self.compression_dict[key] = value
                        self.decompression_dict[value] = key
            
            logger.info(f"Loaded custom dictionaries from {path}")
        except Exception as e:
            logger.error(f"Error loading custom dictionaries: {str(e)}")
    
    def compress(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Compress a prompt using the dictionary-based approach.
        
        Args:
            prompt: The prompt to compress.
            context: Optional context information to aid compression.
            
        Returns:
            The compressed prompt.
        """
        # Sort keys by length in descending order to ensure longer phrases are replaced first
        sorted_keys = sorted(self.compression_dict.keys(), key=len, reverse=True)
        
        compressed_prompt = prompt
        
        # Replace each key with its value
        for key in sorted_keys:
            # Use word boundaries to avoid partial replacements
            # For example, "class" should not be replaced in "subclass"
            pattern = r'\b' + re.escape(key) + r'\b'
            compressed_prompt = re.sub(pattern, self.compression_dict[key], compressed_prompt)
        
        return compressed_prompt
    
    def decompress(self, compressed_prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Decompress a compressed prompt using the dictionary-based approach.
        
        Args:
            compressed_prompt: The compressed prompt to decompress.
            context: Optional context information to aid decompression.
            
        Returns:
            The decompressed prompt.
        """
        # Sort keys by length in descending order to ensure longer phrases are replaced first
        sorted_keys = sorted(self.decompression_dict.keys(), key=len, reverse=True)
        
        decompressed_prompt = compressed_prompt
        
        # Replace each key with its value
        for key in sorted_keys:
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(key) + r'\b'
            decompressed_prompt = re.sub(pattern, self.decompression_dict[key], decompressed_prompt)
        
        return decompressed_prompt
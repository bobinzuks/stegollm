"""
Configuration management for StegoLLM.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
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
        "path": None,  # Will be set to default path during load_config
    },
    "ui": {
        "theme": "dark",
    },
}

def get_default_config_path() -> Path:
    """Get the default configuration path."""
    if os.name == "nt":  # Windows
        config_dir = Path(os.environ.get("APPDATA", "")) / "StegoLLM"
    else:  # Unix-like
        config_dir = Path.home() / ".config" / "stegollm"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.yaml"

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to config file. If None, uses default path.
        
    Returns:
        Dictionary with configuration.
    """
    # Get configuration path
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = get_default_config_path()
    
    # Start with default config
    config = DEFAULT_CONFIG.copy()
    
    # Set default path for custom instructions
    if os.name == "nt":  # Windows
        custom_instructions_dir = Path(os.environ.get("APPDATA", "")) / "StegoLLM"
    else:  # Unix-like
        custom_instructions_dir = Path.home() / ".config" / "stegollm"
    
    config["custom_instructions"]["path"] = str(custom_instructions_dir / "custom_instructions.json")
    
    # Load from file if it exists
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    # Update config with file values (deep merge)
                    config = deep_merge(config, file_config)
        except Exception as e:
            print(f"Error loading config file: {str(e)}")
            print("Using default configuration.")
    else:
        # Create default config file
        save_config(config, config_file)
    
    return config

def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary.
        config_path: Path to config file. If None, uses default path.
    """
    # Get configuration path
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = get_default_config_path()
    
    # Ensure directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to file
    try:
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
        print(f"Error saving config file: {str(e)}")

def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary.
        dict2: Second dictionary.
        
    Returns:
        Merged dictionary.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result
"""
Logging utilities for StegoLLM.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

def setup_logger(name: str, level: str = "info") -> logging.Logger:
    """
    Set up a logger with the given name and level.
    
    Args:
        name: Logger name.
        level: Logging level.
        
    Returns:
        Configured logger instance.
    """
    # Map string levels to logging constants
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    
    # Get the log level
    log_level = level_map.get(level.lower(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Add formatters to handlers
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    
    return logger


def get_log_file_path() -> Path:
    """
    Get the path to the log file.
    
    Returns:
        Path to the log file.
    """
    if os.name == "nt":  # Windows
        log_dir = Path(os.environ.get("APPDATA", "")) / "StegoLLM" / "logs"
    else:  # Unix-like
        log_dir = Path.home() / ".local" / "share" / "stegollm" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "stegollm.log"


def enable_file_logging(logger: logging.Logger, level: str = "info") -> None:
    """
    Enable file logging for the given logger.
    
    Args:
        logger: Logger instance.
        level: Logging level.
    """
    # Map string levels to logging constants
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    
    # Get the log level
    log_level = level_map.get(level.lower(), logging.INFO)
    
    # Get log file path
    log_file = get_log_file_path()
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Add formatter to handler
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)


def get_all_logs() -> str:
    """
    Get all logs from the log file.
    
    Returns:
        Log contents.
    """
    log_file = get_log_file_path()
    
    if log_file.exists():
        with open(log_file, "r") as f:
            return f.read()
    
    return "No logs found."
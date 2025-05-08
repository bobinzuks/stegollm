#!/usr/bin/env python3
"""
Demo script for StegoLLM.

This script demonstrates the compression capabilities of StegoLLM by
applying various compression strategies to sample prompts.
"""

import os
import sys
import json
from typing import Dict, Any, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from stegollm.config.settings import load_config
from stegollm.core.stego_engine import StegoEngine
from stegollm.strategies.dictionary import DictionaryStrategy
from stegollm.utils.logging import setup_logger

# Setup console
console = Console()

# Sample prompts for testing
SAMPLE_PROMPTS = [
    "Write a function to implement quicksort in Python with detailed comments and error handling.",
    "Explain how to optimize database queries for better performance in a production environment with large datasets.",
    "Create a class for handling authentication in a web application using TypeScript and React with secure token management.",
    "What is the difference between synchronous and asynchronous programming? Provide examples in JavaScript.",
    "How do I implement a RESTful API in Node.js with Express? Include authentication and database integration."
]

def create_custom_dictionary():
    """Create a sample custom dictionary for demonstration."""
    custom_dict = {
        "rules": [
            {"pattern": "Write a function", "replacement": "WF:"},
            {"pattern": "Explain how", "replacement": "EH:"},
            {"pattern": "Create a class", "replacement": "CC:"},
            {"pattern": "What is the difference", "replacement": "WID:"},
            {"pattern": "How do I implement", "replacement": "HDII:"}
        ],
        "dictionaries": [
            {
                "name": "programming_terms",
                "entries": {
                    "function": "fn",
                    "algorithm": "algo",
                    "implementation": "impl",
                    "application": "app",
                    "database": "db",
                    "authentication": "auth",
                    "environment": "env",
                    "performance": "perf",
                    "management": "mgmt",
                    "integration": "integ",
                    "synchronous": "sync",
                    "asynchronous": "async",
                    "optimize": "opt",
                    "detailed": "dtl",
                    "JavaScript": "JS",
                    "TypeScript": "TS",
                    "Python": "PY",
                    "Node.js": "Node",
                    "React": "Rct",
                    "Express": "Exp"
                }
            }
        ]
    }
    
    return custom_dict

def run_demo():
    """Run the demonstration."""
    console.print("\n[bold green]StegoLLM Compression Demonstration[/bold green]\n")
    
    # Load config
    config = load_config()
    
    # Create a temporary custom dictionary file
    custom_dict = create_custom_dictionary()
    temp_file = Path("temp_custom_dict.json")
    with open(temp_file, "w") as f:
        json.dump(custom_dict, f, indent=2)
    
    # Set custom dictionary path in config
    config["custom_instructions"]["path"] = str(temp_file)
    
    try:
        # Create strategies
        dictionary_strategy = DictionaryStrategy(config)
        
        # Create table for results
        table = Table(title="Compression Results")
        table.add_column("Original Prompt", style="cyan")
        table.add_column("Compressed", style="green")
        table.add_column("Original Size", justify="right", style="blue")
        table.add_column("Compressed Size", justify="right", style="blue")
        table.add_column("Savings", justify="right", style="purple")
        table.add_column("Ratio", justify="right", style="red")
        
        total_original = 0
        total_compressed = 0
        
        # Process each sample prompt
        for prompt in SAMPLE_PROMPTS:
            # Compress with dictionary strategy
            compressed = dictionary_strategy.compress(prompt)
            
            # Calculate statistics
            original_size = len(prompt)
            compressed_size = len(compressed)
            savings = original_size - compressed_size
            ratio = (savings / original_size) * 100
            
            # Add to totals
            total_original += original_size
            total_compressed += compressed_size
            
            # Add to table
            table.add_row(
                prompt[:40] + "..." if len(prompt) > 40 else prompt,
                compressed[:40] + "..." if len(compressed) > 40 else compressed,
                str(original_size),
                str(compressed_size),
                str(savings),
                f"{ratio:.2f}%"
            )
        
        # Add summary row
        total_savings = total_original - total_compressed
        total_ratio = (total_savings / total_original) * 100
        table.add_row(
            "[bold]TOTAL[/bold]",
            "",
            f"[bold]{total_original}[/bold]",
            f"[bold]{total_compressed}[/bold]",
            f"[bold]{total_savings}[/bold]",
            f"[bold]{total_ratio:.2f}%[/bold]"
        )
        
        # Print the table
        console.print(table)
        
        # Print detailed example
        console.print("\n[bold yellow]Detailed Example:[/bold yellow]")
        example = SAMPLE_PROMPTS[0]
        compressed_example = dictionary_strategy.compress(example)
        
        console.print(f"\n[bold cyan]Original:[/bold cyan] {example}")
        console.print(f"[bold green]Compressed:[/bold green] {compressed_example}")
        console.print(f"[bold purple]Savings:[/bold purple] {len(example) - len(compressed_example)} characters")
        console.print(f"[bold red]Compression Ratio:[/bold red] {((len(example) - len(compressed_example)) / len(example) * 100):.2f}%")
        
        console.print("\n[bold]This demonstrates how StegoLLM can significantly reduce the size of prompts[/bold]")
        console.print("[bold]sent to LLM APIs, saving on token usage and costs.[/bold]")
        
    finally:
        # Clean up temporary file
        if temp_file.exists():
            temp_file.unlink()

if __name__ == "__main__":
    run_demo()
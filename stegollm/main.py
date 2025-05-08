#!/usr/bin/env python3
"""
StegoLLM: A local proxy for compressing LLM prompts using steganography.

This module serves as the entry point for the StegoLLM application.
"""

import os
import sys
import typer
import uvicorn
from rich.console import Console
from rich import print as rprint

from stegollm.core.proxy import ProxyServer
from stegollm.config.settings import load_config

app = typer.Typer(help="StegoLLM: A local proxy for compressing LLM prompts.")
console = Console()

@app.command()
def start(
    port: int = typer.Option(8080, "--port", "-p", help="Port to run the proxy server on"),
    config_path: str = typer.Option(
        None, "--config", "-c", help="Path to config file (default: ~/.config/stegollm/config.yaml)"
    ),
    ui_port: int = typer.Option(8081, "--ui-port", "-u", help="Port to run the web UI on"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
):
    """Start the StegoLLM proxy server."""
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Set up proxy server
        proxy = ProxyServer(config, port=port, ui_port=ui_port, verbose=verbose)
        
        # Display banner
        display_banner(port, ui_port)
        
        # Start proxy server
        proxy.start()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def version():
    """Display the StegoLLM version."""
    from stegollm import __version__
    console.print(f"StegoLLM v{__version__}")


def display_banner(port: int, ui_port: int):
    """Display the StegoLLM banner."""
    rprint(f"""
[bold green]╔══════════════════════════════════════════════════╗[/bold green]
[bold green]║                    [bold white]StegoLLM[/bold white]                     ║[/bold green]
[bold green]║ [bold white]A local proxy for compressing LLM prompts[/bold white]       ║[/bold green]
[bold green]╚══════════════════════════════════════════════════╝[/bold green]

🔄 Proxy server running on [bold cyan]http://localhost:{port}[/bold cyan]
🌐 Web UI available at [bold cyan]http://localhost:{ui_port}[/bold cyan]

[bold yellow]Status:[/bold yellow] 🟢 Compression active

Configure VS Code to use this proxy:
1. Open VS Code settings
2. Set "http.proxy" to "http://localhost:{port}"

Press [bold red]Ctrl+C[/bold red] to stop the server
""")


def main():
    """Run the application."""
    app()


if __name__ == "__main__":
    main()
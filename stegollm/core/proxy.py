"""
Proxy server implementation for StegoLLM.

This module contains the ProxyServer class that intercepts traffic between
VS Code and LLM APIs, compressing prompts and decompressing responses.
"""

import os
import sys
import threading
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
import asyncio
from pathlib import Path

from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import http
from mitmproxy import ctx
from fastapi import FastAPI
import uvicorn

from stegollm.core.stego_engine import StegoEngine
from stegollm.api_compat.detector import ApiDetector
from stegollm.utils.logging import setup_logger

# Setup logger
logger = setup_logger(__name__)

class StegoLLMInterceptor:
    """
    MITMProxy addon for intercepting LLM API traffic.
    """
    
    def __init__(self, config: Dict[str, Any], stego_engine: StegoEngine, api_detector: ApiDetector):
        """
        Initialize the interceptor.
        
        Args:
            config: Configuration dictionary.
            stego_engine: StegoEngine instance.
            api_detector: ApiDetector instance.
        """
        self.config = config
        self.stego_engine = stego_engine
        self.api_detector = api_detector
        self.compression_enabled = config["compression"]["enabled"]
        self.metrics = {"requests": 0, "compressed_size": 0, "original_size": 0}
    
    def request(self, flow: http.HTTPFlow) -> None:
        """
        Process an HTTP request.
        
        Args:
            flow: MITMProxy flow.
        """
        # Skip if compression is disabled
        if not self.compression_enabled:
            logger.info("Compression disabled, passing through request.")
            return
        
        try:
            # Check if this is an LLM API request
            api_type = self.api_detector.detect_api(flow)
            
            if api_type:
                logger.info(f"Detected {api_type} API request.")
                self.metrics["requests"] += 1
                
                # Extract the prompt from the request
                prompt, prompt_path = self.api_detector.extract_prompt(flow, api_type)
                
                if prompt:
                    # Log original size
                    original_size = len(prompt)
                    self.metrics["original_size"] += original_size
                    logger.info(f"Original prompt size: {original_size} characters.")
                    
                    # Compress the prompt
                    compressed_prompt = self.stego_engine.compress(prompt)
                    
                    # Log compressed size
                    compressed_size = len(compressed_prompt)
                    self.metrics["compressed_size"] += compressed_size
                    compression_ratio = (original_size - compressed_size) / original_size * 100
                    logger.info(f"Compressed prompt size: {compressed_size} characters.")
                    logger.info(f"Compression ratio: {compression_ratio:.2f}%.")
                    
                    # Update the request with the compressed prompt
                    self.api_detector.update_prompt(flow, api_type, compressed_prompt, prompt_path)
                    
                    logger.info("Request compressed successfully.")
                else:
                    logger.warning("Could not extract prompt from request.")
            else:
                logger.debug("Not an LLM API request, passing through.")
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
    
    def response(self, flow: http.HTTPFlow) -> None:
        """
        Process an HTTP response.
        
        Args:
            flow: MITMProxy flow.
        """
        # Skip if compression is disabled
        if not self.compression_enabled:
            logger.info("Compression disabled, passing through response.")
            return
        
        try:
            # Check if this is an LLM API response
            api_type = self.api_detector.detect_api(flow)
            
            if api_type:
                logger.info(f"Detected {api_type} API response.")
                
                # Extract the response from the response
                response_text, response_path = self.api_detector.extract_response(flow, api_type)
                
                if response_text:
                    # Decompress the response if needed
                    # (In most cases, no decompression is needed for the response,
                    # but we might need to transform it in some way)
                    transformed_response = self.stego_engine.transform_response(response_text)
                    
                    # Update the response
                    self.api_detector.update_response(flow, api_type, transformed_response, response_path)
                    
                    logger.info("Response processed successfully.")
                else:
                    logger.warning("Could not extract response from response.")
            else:
                logger.debug("Not an LLM API response, passing through.")
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")


class ProxyServer:
    """
    Proxy server that intercepts traffic between VS Code and LLM APIs.
    """
    
    def __init__(
        self, 
        config: Dict[str, Any], 
        port: int = 8080, 
        ui_port: int = 8081, 
        verbose: bool = False
    ):
        """
        Initialize the proxy server.
        
        Args:
            config: Configuration dictionary.
            port: Port to run the proxy server on.
            ui_port: Port to run the web UI on.
            verbose: Enable verbose logging.
        """
        self.config = config
        self.port = port
        self.ui_port = ui_port
        self.verbose = verbose
        
        # Initialize components
        self.stego_engine = StegoEngine(config)
        self.api_detector = ApiDetector(config)
        
        # Set up proxy options
        self.opts = options.Options(
            listen_host="127.0.0.1",
            listen_port=port,
            ssl_insecure=True,  # Allow self-signed certificates
        )
        
        # Create proxy master
        self.master = DumpMaster(self.opts)
        
        # Add interceptor addon
        self.interceptor = StegoLLMInterceptor(config, self.stego_engine, self.api_detector)
        self.master.addons.add(self.interceptor)
        
        # Set up web UI
        self.app = FastAPI(title="StegoLLM", description="Web UI for StegoLLM")
        
        # Import UI routes
        from stegollm.ui.web.routes import setup_routes
        setup_routes(self.app, self)
        
        # Web UI thread
        self.ui_thread = None
    
    def start(self):
        """Start the proxy server and web UI."""
        # Start web UI in a separate thread
        self.ui_thread = threading.Thread(target=self._start_web_ui)
        self.ui_thread.daemon = True
        self.ui_thread.start()
        
        # Start proxy server
        try:
            logger.info(f"Starting proxy server on port {self.port}.")
            logger.info(f"Web UI available at http://localhost:{self.ui_port}")
            
            # Set compression status indicator
            status = "🟢" if self.config["compression"]["enabled"] else "🔴"
            logger.info(f"Compression status: {status}")
            
            # Run the proxy
            self.master.run()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the proxy server."""
        logger.info("Stopping proxy server...")
        self.master.shutdown()
        logger.info("Proxy server stopped.")
    
    def _start_web_ui(self):
        """Start the web UI server."""
        logger.info(f"Starting web UI on port {self.ui_port}.")
        
        # Run the UI server
        uvicorn.run(self.app, host="127.0.0.1", port=self.ui_port, log_level="info")
"""
End-to-end tests for StegoLLM.
"""

import os
import json
import time
import threading
import pytest
import requests
from unittest.mock import MagicMock, patch

from stegollm.core.proxy import ProxyServer, StegoLLMInterceptor
from stegollm.config.settings import load_config
from stegollm.core.stego_engine import StegoEngine
from stegollm.strategies.dictionary import DictionaryStrategy

# Skip these tests by default because they start actual servers
# Run with pytest -xvs tests/test_end_to_end.py to run them
pytestmark = pytest.mark.skip(reason="End-to-end tests start actual servers")

class TestEndToEnd:
    """End-to-end tests for StegoLLM."""
    
    @pytest.fixture
    def proxy_server(self):
        """Create a proxy server for testing."""
        # Load config
        config = {
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
                "path": None,
            },
            "ui": {
                "theme": "dark",
            },
        }
        
        # Create server with mock components for easier testing
        server = ProxyServer(config, port=8888, ui_port=8889)
        
        # Mock the master to avoid actually starting mitmproxy
        server.master = MagicMock()
        
        # Return the server
        yield server
        
        # Clean up
        server.stop()
    
    def test_dictionary_compression(self, proxy_server):
        """Test that dictionary compression works end-to-end."""
        # Create a dictionary strategy
        strategy = DictionaryStrategy(proxy_server.config)
        
        # Test with a simple prompt
        prompt = "Write a function to calculate the Fibonacci sequence in Python"
        
        # Compress using the strategy
        compressed = strategy.compress(prompt)
        
        # Verify compression actually happened
        assert len(compressed) < len(prompt)
        
        # Decompress
        decompressed = strategy.decompress(compressed)
        
        # Verify decompression worked
        assert decompressed == prompt
        
        print(f"Original: '{prompt}' ({len(prompt)} chars)")
        print(f"Compressed: '{compressed}' ({len(compressed)} chars)")
        print(f"Compression ratio: {(1 - len(compressed) / len(prompt)) * 100:.2f}%")
    
    @patch('mitmproxy.http.HTTPFlow')
    def test_openai_api_interception(self, mock_flow, proxy_server):
        """Test that the OpenAI API is intercepted correctly."""
        # Create mock request data
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Write a function to calculate Fibonacci numbers."}
            ]
        }
        
        # Create mock flow
        mock_flow.request = MagicMock()
        mock_flow.request.url = "https://api.openai.com/v1/chat/completions"
        mock_flow.request.content = json.dumps(request_data).encode("utf-8")
        mock_flow.request.headers = {"content-length": str(len(mock_flow.request.content))}
        
        # Process the request
        proxy_server.interceptor.request(mock_flow)
        
        # Get the processed request content
        processed_data = json.loads(mock_flow.request.content.decode("utf-8"))
        
        # Verify the prompt was compressed
        original_prompt = request_data["messages"][1]["content"]
        compressed_prompt = processed_data["messages"][1]["content"]
        
        assert len(compressed_prompt) < len(original_prompt)
        
        print(f"Original prompt: '{original_prompt}' ({len(original_prompt)} chars)")
        print(f"Compressed prompt: '{compressed_prompt}' ({len(compressed_prompt)} chars)")
        print(f"Compression ratio: {(1 - len(compressed_prompt) / len(original_prompt)) * 100:.2f}%")
    
    @pytest.mark.manual
    def test_proxy_server_startup(self, proxy_server):
        """
        Test that the proxy server starts correctly.
        
        This test is marked as manual because it starts actual servers.
        """
        # Start the server in a separate thread
        thread = threading.Thread(target=proxy_server.start)
        thread.daemon = True
        thread.start()
        
        # Wait for the server to start
        time.sleep(2)
        
        try:
            # Test the web UI is running
            response = requests.get("http://localhost:8889/")
            assert response.status_code == 200
            
            # Test API endpoint
            response = requests.get("http://localhost:8889/api/status")
            assert response.status_code == 200
            data = response.json()
            assert "compression_enabled" in data
            
            print("Proxy server started successfully")
            print(f"Web UI available at http://localhost:8889")
            print(f"Proxy running on port 8888")
        finally:
            # Stop the server
            proxy_server.stop()

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
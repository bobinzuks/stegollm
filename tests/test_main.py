"""
Tests for the main module.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock

import stegollm.main

def test_version_command():
    """Test the version command."""
    with patch.object(sys, 'argv', ['stegollm', 'version']), \
         patch('rich.console.Console.print') as mock_print:
        # Run the main function
        try:
            stegollm.main.main()
        except SystemExit:
            pass
        
        # Check that the version was printed
        mock_print.assert_called_once()
        assert "StegoLLM v" in mock_print.call_args[0][0]

@patch('stegollm.core.proxy.ProxyServer')
@patch('stegollm.config.settings.load_config')
def test_start_command(mock_load_config, mock_proxy_server):
    """Test the start command."""
    # Mock the config
    mock_config = {
        "compression": {
            "enabled": True,
            "strategy": "dictionary",
            "deep_learning_enabled": False,
        }
    }
    mock_load_config.return_value = mock_config
    
    # Mock the proxy server
    mock_instance = MagicMock()
    mock_proxy_server.return_value = mock_instance
    
    # Run the start command
    with patch.object(sys, 'argv', ['stegollm', 'start', '--port', '8888']):
        try:
            stegollm.main.main()
        except SystemExit:
            pass
    
    # Check that the proxy server was started with the correct port
    mock_proxy_server.assert_called_once_with(
        mock_config, port=8888, ui_port=8081, verbose=False
    )
    mock_instance.start.assert_called_once()

@patch('stegollm.core.proxy.ProxyServer')
@patch('stegollm.config.settings.load_config')
def test_custom_config_path(mock_load_config, mock_proxy_server):
    """Test using a custom config path."""
    # Mock the config
    mock_config = {
        "compression": {
            "enabled": True,
            "strategy": "dictionary",
            "deep_learning_enabled": False,
        }
    }
    mock_load_config.return_value = mock_config
    
    # Run the start command with custom config path
    with patch.object(sys, 'argv', ['stegollm', 'start', '--config', 'custom_config.yaml']):
        try:
            stegollm.main.main()
        except SystemExit:
            pass
    
    # Check that load_config was called with the custom path
    mock_load_config.assert_called_once_with('custom_config.yaml')

@patch('stegollm.core.proxy.ProxyServer')
@patch('stegollm.config.settings.load_config')
def test_exception_handling(mock_load_config, mock_proxy_server):
    """Test that exceptions are handled properly."""
    # Make load_config raise an exception
    mock_load_config.side_effect = Exception("Test error")
    
    # Mock the console
    mock_console = MagicMock()
    
    # Run the start command
    with patch.object(sys, 'argv', ['stegollm', 'start']), \
         patch('rich.console.Console', return_value=mock_console), \
         patch('sys.exit') as mock_exit:
        stegollm.main.main()
    
    # Check that the error was printed and sys.exit was called
    mock_console.print.assert_called_once()
    assert "Error" in mock_console.print.call_args[0][0]
    mock_exit.assert_called_once_with(1)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
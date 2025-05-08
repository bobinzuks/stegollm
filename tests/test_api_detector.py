"""
Tests for the API detector.
"""

import json
import pytest
from unittest.mock import MagicMock
from mitmproxy.http import HTTPFlow, HTTPRequest, HTTPResponse
from mitmproxy import http

from stegollm.api_compat.detector import ApiDetector

def create_mock_flow(url, request_content=None, response_content=None):
    """Create a mock HTTPFlow for testing."""
    # Create mock request
    mock_request = MagicMock(spec=HTTPRequest)
    mock_request.url = url
    if request_content:
        mock_request.content = json.dumps(request_content).encode("utf-8")
    else:
        mock_request.content = b"{}"
    mock_request.headers = {"content-length": str(len(mock_request.content))}
    
    # Create mock flow
    mock_flow = MagicMock(spec=HTTPFlow)
    mock_flow.request = mock_request
    
    # Add response if provided
    if response_content:
        mock_response = MagicMock(spec=HTTPResponse)
        mock_response.content = json.dumps(response_content).encode("utf-8")
        mock_response.headers = {"content-length": str(len(mock_response.content))}
        mock_flow.response = mock_response
    
    return mock_flow

def test_detect_api(sample_config):
    """Test API detection for different API types."""
    detector = ApiDetector(sample_config)
    
    # Test OpenAI API detection
    openai_flow = create_mock_flow("https://api.openai.com/v1/chat/completions")
    api_type = detector.detect_api(openai_flow)
    assert api_type == "openai"
    
    # Test Claude API detection
    claude_flow = create_mock_flow("https://api.anthropic.com/v1/messages")
    api_type = detector.detect_api(claude_flow)
    assert api_type == "claude"
    
    # Test Gemini API detection
    gemini_flow = create_mock_flow("https://generativelanguage.googleapis.com/v1/models/gemini-pro/generateContent")
    api_type = detector.detect_api(gemini_flow)
    assert api_type == "gemini"
    
    # Test non-LLM API detection
    other_flow = create_mock_flow("https://example.com/api/data")
    api_type = detector.detect_api(other_flow)
    assert api_type is None

def test_extract_openai_prompt(sample_config):
    """Test extracting prompts from OpenAI API requests."""
    detector = ApiDetector(sample_config)
    
    # Test chat completion
    chat_content = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a function to calculate fibonacci numbers."}
        ]
    }
    chat_flow = create_mock_flow(
        "https://api.openai.com/v1/chat/completions",
        request_content=chat_content
    )
    prompt, path = detector.extract_prompt(chat_flow, "openai")
    assert prompt == "Write a function to calculate fibonacci numbers."
    assert path == ["messages", 1, "content"]
    
    # Test completion
    completion_content = {
        "model": "davinci",
        "prompt": "Write a function to calculate fibonacci numbers."
    }
    completion_flow = create_mock_flow(
        "https://api.openai.com/v1/completions",
        request_content=completion_content
    )
    prompt, path = detector.extract_prompt(completion_flow, "openai")
    assert prompt == "Write a function to calculate fibonacci numbers."
    assert path == ["prompt"]

def test_extract_claude_prompt(sample_config):
    """Test extracting prompts from Claude API requests."""
    detector = ApiDetector(sample_config)
    
    # Test messages
    messages_content = {
        "model": "claude-2.0",
        "messages": [
            {"role": "user", "content": "Write a function to calculate fibonacci numbers."}
        ]
    }
    messages_flow = create_mock_flow(
        "https://api.anthropic.com/v1/messages",
        request_content=messages_content
    )
    prompt, path = detector.extract_prompt(messages_flow, "claude")
    assert prompt == "Write a function to calculate fibonacci numbers."
    assert path == ["messages", 0, "content"]
    
    # Test completion
    completion_content = {
        "model": "claude-instant-1.0",
        "prompt": "Write a function to calculate fibonacci numbers."
    }
    completion_flow = create_mock_flow(
        "https://api.anthropic.com/v1/complete",
        request_content=completion_content
    )
    prompt, path = detector.extract_prompt(completion_flow, "claude")
    assert prompt == "Write a function to calculate fibonacci numbers."
    assert path == ["prompt"]

def test_extract_gemini_prompt(sample_config):
    """Test extracting prompts from Gemini API requests."""
    detector = ApiDetector(sample_config)
    
    # Test generateContent
    content = {
        "contents": [
            {
                "parts": [
                    {"text": "Write a function to calculate fibonacci numbers."}
                ]
            }
        ]
    }
    flow = create_mock_flow(
        "https://generativelanguage.googleapis.com/v1/models/gemini-pro/generateContent",
        request_content=content
    )
    prompt, path = detector.extract_prompt(flow, "gemini")
    assert prompt == "Write a function to calculate fibonacci numbers."
    assert path == ["contents", 0, "parts", 0, "text"]

def test_update_prompt(sample_config):
    """Test updating prompts in requests."""
    detector = ApiDetector(sample_config)
    
    # Test updating OpenAI chat completion
    chat_content = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a function to calculate fibonacci numbers."}
        ]
    }
    chat_flow = create_mock_flow(
        "https://api.openai.com/v1/chat/completions",
        request_content=chat_content
    )
    
    # Extract prompt and path
    prompt, path = detector.extract_prompt(chat_flow, "openai")
    
    # Update prompt
    compressed_prompt = "Write a fn to calc fib nums."
    detector.update_prompt(chat_flow, "openai", compressed_prompt, path)
    
    # Verify update
    updated_content = json.loads(chat_flow.request.content.decode("utf-8"))
    assert updated_content["messages"][1]["content"] == compressed_prompt
    
    # Verify content-length header was updated
    assert chat_flow.request.headers["content-length"] == str(len(chat_flow.request.content))

def test_extract_response(sample_config):
    """Test extracting responses from API responses."""
    detector = ApiDetector(sample_config)
    
    # Test OpenAI chat completion response
    chat_response = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Here is a function to calculate Fibonacci numbers..."
                },
                "finish_reason": "stop"
            }
        ]
    }
    chat_flow = create_mock_flow(
        "https://api.openai.com/v1/chat/completions",
        response_content=chat_response
    )
    
    response, path = detector.extract_response(chat_flow, "openai")
    assert response == "Here is a function to calculate Fibonacci numbers..."
    assert path == ["choices", 0, "message", "content"]
    
    # Test Claude response
    claude_response = {
        "id": "msg_123",
        "content": "Here is a function to calculate Fibonacci numbers..."
    }
    claude_flow = create_mock_flow(
        "https://api.anthropic.com/v1/messages",
        response_content=claude_response
    )
    
    response, path = detector.extract_response(claude_flow, "claude")
    assert response == "Here is a function to calculate Fibonacci numbers..."
    assert path == ["content"]
    
    # Test Gemini response
    gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "Here is a function to calculate Fibonacci numbers..."}
                    ]
                }
            }
        ]
    }
    gemini_flow = create_mock_flow(
        "https://generativelanguage.googleapis.com/v1/models/gemini-pro/generateContent",
        response_content=gemini_response
    )
    
    response, path = detector.extract_response(gemini_flow, "gemini")
    assert response == "Here is a function to calculate Fibonacci numbers..."
    assert path == ["candidates", 0, "content", "parts", 0, "text"]

def test_update_response(sample_config):
    """Test updating responses in API responses."""
    detector = ApiDetector(sample_config)
    
    # Test updating OpenAI chat completion response
    chat_response = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Here is a function to calculate Fibonacci numbers..."
                },
                "finish_reason": "stop"
            }
        ]
    }
    chat_flow = create_mock_flow(
        "https://api.openai.com/v1/chat/completions",
        response_content=chat_response
    )
    
    # Extract response and path
    response, path = detector.extract_response(chat_flow, "openai")
    
    # Update response
    modified_response = "Here is an optimized function to calculate Fibonacci numbers..."
    detector.update_response(chat_flow, "openai", modified_response, path)
    
    # Verify update
    updated_content = json.loads(chat_flow.response.content.decode("utf-8"))
    assert updated_content["choices"][0]["message"]["content"] == modified_response
    
    # Verify content-length header was updated
    assert chat_flow.response.headers["content-length"] == str(len(chat_flow.response.content))

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
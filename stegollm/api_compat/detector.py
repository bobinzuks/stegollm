"""
API format detector for StegoLLM.

This module contains the ApiDetector class that detects the LLM API format
of a request or response and extracts/updates the prompt/response.
"""

import json
import re
from typing import Dict, Any, Optional, List, Tuple, Union
from mitmproxy import http

from stegollm.utils.logging import setup_logger

# Setup logger
logger = setup_logger(__name__)

class ApiDetector:
    """
    API format detector for identifying LLM API calls and extracting/updating prompts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the detector.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.enabled_apis = config.get("api_compat", {}).get("supported_apis", ["openai", "claude", "gemini"])
    
    def detect_api(self, flow: http.HTTPFlow) -> Optional[str]:
        """
        Detect the LLM API format of a request or response.
        
        Args:
            flow: MITMProxy flow.
            
        Returns:
            API type if detected, None otherwise.
        """
        # Check if API compatibility is enabled
        if not self.config.get("api_compat", {}).get("enabled", True):
            return None
        
        # Get the URL
        url = flow.request.url
        
        # Check OpenAI API
        if "openai" in self.enabled_apis and "api.openai.com" in url:
            # Check if it's a chat or completion endpoint
            if "/v1/chat/completions" in url or "/v1/completions" in url:
                return "openai"
        
        # Check Claude API
        if "claude" in self.enabled_apis and "anthropic.com" in url:
            # Check if it's a message or completion endpoint
            if "/v1/messages" in url or "/v1/complete" in url:
                return "claude"
        
        # Check Gemini API
        if "gemini" in self.enabled_apis and "generativelanguage.googleapis.com" in url:
            # Check if it's a generate endpoint
            if "/v1/models" in url and "/generateContent" in url:
                return "gemini"
        
        # No matching API found
        return None
    
    def extract_prompt(self, flow: http.HTTPFlow, api_type: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract the prompt from a request.
        
        Args:
            flow: MITMProxy flow.
            api_type: API type.
            
        Returns:
            Tuple of (prompt, path to prompt in the request).
        """
        try:
            # Get request content as string
            content = flow.request.content.decode("utf-8")
            
            # Parse JSON
            data = json.loads(content)
            
            if api_type == "openai":
                return self._extract_openai_prompt(data)
            elif api_type == "claude":
                return self._extract_claude_prompt(data)
            elif api_type == "gemini":
                return self._extract_gemini_prompt(data)
            else:
                logger.warning(f"Unknown API type: {api_type}")
                return None, None
        except Exception as e:
            logger.error(f"Error extracting prompt: {str(e)}")
            return None, None
    
    def _extract_openai_prompt(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract the prompt from an OpenAI API request.
        
        Args:
            data: Request data.
            
        Returns:
            Tuple of (prompt, path to prompt in the request).
        """
        # Check if it's a chat completion
        if "messages" in data:
            # Get the last user message
            for i, message in enumerate(reversed(data["messages"])):
                if message.get("role") == "user":
                    # Found a user message, extract the content
                    return message.get("content"), ["messages", len(data["messages"]) - i - 1, "content"]
            
            # No user message found
            return None, None
        
        # Check if it's a completion
        elif "prompt" in data:
            return data["prompt"], ["prompt"]
        
        # No prompt found
        return None, None
    
    def _extract_claude_prompt(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract the prompt from a Claude API request.
        
        Args:
            data: Request data.
            
        Returns:
            Tuple of (prompt, path to prompt in the request).
        """
        # Check if it's a message
        if "messages" in data:
            # Get the last user message
            for i, message in enumerate(reversed(data["messages"])):
                if message.get("role") == "user":
                    # Found a user message, extract the content
                    return message.get("content"), ["messages", len(data["messages"]) - i - 1, "content"]
            
            # No user message found
            return None, None
        
        # Check if it's a completion
        elif "prompt" in data:
            return data["prompt"], ["prompt"]
        
        # No prompt found
        return None, None
    
    def _extract_gemini_prompt(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract the prompt from a Gemini API request.
        
        Args:
            data: Request data.
            
        Returns:
            Tuple of (prompt, path to prompt in the request).
        """
        # Check for contents
        if "contents" in data:
            # Find the first text part
            for i, content in enumerate(data["contents"]):
                if "parts" in content:
                    for j, part in enumerate(content["parts"]):
                        if "text" in part:
                            return part["text"], ["contents", i, "parts", j, "text"]
        
        # No prompt found
        return None, None
    
    def update_prompt(
        self, 
        flow: http.HTTPFlow, 
        api_type: str, 
        prompt: str, 
        path: Optional[List[str]] = None
    ) -> None:
        """
        Update the prompt in a request.
        
        Args:
            flow: MITMProxy flow.
            api_type: API type.
            prompt: New prompt.
            path: Path to prompt in the request.
        """
        try:
            # Get request content as string
            content = flow.request.content.decode("utf-8")
            
            # Parse JSON
            data = json.loads(content)
            
            # Update the prompt using the path
            if path:
                current = data
                for i, key in enumerate(path):
                    if i == len(path) - 1:
                        # Last key, update the value
                        current[key] = prompt
                    else:
                        # Navigate to the next level
                        current = current[key]
            
            # Update the request
            flow.request.content = json.dumps(data).encode("utf-8")
            
            # Update content-length header
            flow.request.headers["content-length"] = str(len(flow.request.content))
            
            logger.info(f"Updated prompt in {api_type} request.")
        except Exception as e:
            logger.error(f"Error updating prompt: {str(e)}")
    
    def extract_response(self, flow: http.HTTPFlow, api_type: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract the response from a response.
        
        Args:
            flow: MITMProxy flow.
            api_type: API type.
            
        Returns:
            Tuple of (response, path to response in the response).
        """
        try:
            # Get response content as string
            content = flow.response.content.decode("utf-8")
            
            # Parse JSON
            data = json.loads(content)
            
            if api_type == "openai":
                return self._extract_openai_response(data)
            elif api_type == "claude":
                return self._extract_claude_response(data)
            elif api_type == "gemini":
                return self._extract_gemini_response(data)
            else:
                logger.warning(f"Unknown API type: {api_type}")
                return None, None
        except Exception as e:
            logger.error(f"Error extracting response: {str(e)}")
            return None, None
    
    def _extract_openai_response(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract the response from an OpenAI API response.
        
        Args:
            data: Response data.
            
        Returns:
            Tuple of (response, path to response in the response).
        """
        # Check if there are choices
        if "choices" in data and len(data["choices"]) > 0:
            # Check if it's a chat completion
            if "message" in data["choices"][0]:
                return data["choices"][0]["message"].get("content"), ["choices", 0, "message", "content"]
            
            # Check if it's a completion
            elif "text" in data["choices"][0]:
                return data["choices"][0]["text"], ["choices", 0, "text"]
        
        # No response found
        return None, None
    
    def _extract_claude_response(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract the response from a Claude API response.
        
        Args:
            data: Response data.
            
        Returns:
            Tuple of (response, path to response in the response).
        """
        # Check if it's a message
        if "content" in data:
            return data["content"], ["content"]
        
        # Check if it's a completion
        elif "completion" in data:
            return data["completion"], ["completion"]
        
        # No response found
        return None, None
    
    def _extract_gemini_response(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract the response from a Gemini API response.
        
        Args:
            data: Response data.
            
        Returns:
            Tuple of (response, path to response in the response).
        """
        # Check for candidates
        if "candidates" in data and len(data["candidates"]) > 0:
            # Find the first text part
            if "content" in data["candidates"][0]:
                content = data["candidates"][0]["content"]
                if "parts" in content:
                    for i, part in enumerate(content["parts"]):
                        if "text" in part:
                            return part["text"], ["candidates", 0, "content", "parts", i, "text"]
        
        # No response found
        return None, None
    
    def update_response(
        self, 
        flow: http.HTTPFlow, 
        api_type: str, 
        response: str, 
        path: Optional[List[str]] = None
    ) -> None:
        """
        Update the response in a response.
        
        Args:
            flow: MITMProxy flow.
            api_type: API type.
            response: New response.
            path: Path to response in the response.
        """
        try:
            # Get response content as string
            content = flow.response.content.decode("utf-8")
            
            # Parse JSON
            data = json.loads(content)
            
            # Update the response using the path
            if path:
                current = data
                for i, key in enumerate(path):
                    if i == len(path) - 1:
                        # Last key, update the value
                        current[key] = response
                    else:
                        # Navigate to the next level
                        current = current[key]
            
            # Update the response
            flow.response.content = json.dumps(data).encode("utf-8")
            
            # Update content-length header
            flow.response.headers["content-length"] = str(len(flow.response.content))
            
            logger.info(f"Updated response in {api_type} response.")
        except Exception as e:
            logger.error(f"Error updating response: {str(e)}")
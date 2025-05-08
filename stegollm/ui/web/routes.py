"""
Web routes for the StegoLLM UI.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from stegollm.utils.logging import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Create router
router = APIRouter()

# Get template directory
package_dir = Path(__file__).parent
templates = Jinja2Templates(directory=str(package_dir / "templates"))

# Models for API requests
class CompressionToggle(BaseModel):
    enabled: bool

class DeepLearningToggle(BaseModel):
    enabled: bool

class StrategyChange(BaseModel):
    strategy: str

class StegoUIHandler:
    """
    Handler for the web UI routes.
    """
    
    def __init__(self, proxy_server):
        """
        Initialize the handler.
        
        Args:
            proxy_server: The proxy server instance.
        """
        self.proxy_server = proxy_server
    
    async def index(self, request: Request):
        """
        Render the dashboard page.
        
        Args:
            request: FastAPI request object.
        
        Returns:
            The rendered template.
        """
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "status": {
                    "compression_enabled": self.proxy_server.config["compression"]["enabled"],
                    "strategy": self.proxy_server.config["compression"]["strategy"],
                    "deep_learning_enabled": self.proxy_server.config["compression"]["deep_learning_enabled"]
                },
                "metrics": self.proxy_server.interceptor.metrics,
                "proxy_port": self.proxy_server.port,
                "ui_port": self.proxy_server.ui_port
            }
        )
    
    async def settings(self, request: Request):
        """
        Render the settings page.
        
        Args:
            request: FastAPI request object.
        
        Returns:
            The rendered template.
        """
        return templates.TemplateResponse(
            "settings.html",
            {
                "request": request,
                "config": self.proxy_server.config,
                "proxy_port": self.proxy_server.port,
                "ui_port": self.proxy_server.ui_port
            }
        )
    
    async def statistics(self, request: Request):
        """
        Render the statistics page.
        
        Args:
            request: FastAPI request object.
        
        Returns:
            The rendered template.
        """
        return templates.TemplateResponse(
            "statistics.html",
            {
                "request": request,
                "metrics": self.proxy_server.interceptor.metrics,
                "proxy_port": self.proxy_server.port,
                "ui_port": self.proxy_server.ui_port
            }
        )
    
    async def custom_instructions(self, request: Request):
        """
        Render the custom instructions page.
        
        Args:
            request: FastAPI request object.
        
        Returns:
            The rendered template.
        """
        # Load custom instructions if they exist
        custom_instructions = {}
        custom_path = self.proxy_server.config.get("custom_instructions", {}).get("path")
        
        if custom_path:
            try:
                custom_file = Path(custom_path)
                if custom_file.exists():
                    with open(custom_file, "r") as f:
                        custom_instructions = json.load(f)
            except Exception as e:
                logger.error(f"Error loading custom instructions: {str(e)}")
        
        return templates.TemplateResponse(
            "custom_instructions.html",
            {
                "request": request,
                "custom_instructions": custom_instructions,
                "proxy_port": self.proxy_server.port,
                "ui_port": self.proxy_server.ui_port
            }
        )
    
    async def get_status(self):
        """
        Get the current status.
        
        Returns:
            JSON response with status.
        """
        return {
            "compression_enabled": self.proxy_server.config["compression"]["enabled"],
            "strategy": self.proxy_server.config["compression"]["strategy"],
            "deep_learning_enabled": self.proxy_server.config["compression"]["deep_learning_enabled"],
            "metrics": self.proxy_server.interceptor.metrics,
        }
    
    async def toggle_compression(self, data: CompressionToggle):
        """
        Toggle compression.
        
        Args:
            data: Toggle data.
        
        Returns:
            JSON response with result.
        """
        self.proxy_server.config["compression"]["enabled"] = data.enabled
        self.proxy_server.interceptor.compression_enabled = data.enabled
        
        logger.info(f"Compression {'enabled' if data.enabled else 'disabled'}")
        
        return {
            "compression_enabled": data.enabled,
            "message": f"Compression {'enabled' if data.enabled else 'disabled'}"
        }
    
    async def toggle_deep_learning(self, data: DeepLearningToggle):
        """
        Toggle deep learning.
        
        Args:
            data: Toggle data.
        
        Returns:
            JSON response with result.
        """
        self.proxy_server.stego_engine.toggle_deep_learning(data.enabled)
        
        return {
            "deep_learning_enabled": self.proxy_server.config["compression"]["deep_learning_enabled"],
            "message": f"Deep learning {'enabled' if data.enabled else 'disabled'}"
        }
    
    async def change_strategy(self, data: StrategyChange):
        """
        Change the compression strategy.
        
        Args:
            data: Strategy data.
        
        Returns:
            JSON response with result.
        """
        try:
            self.proxy_server.stego_engine.set_strategy(data.strategy)
            
            return {
                "strategy": data.strategy,
                "message": f"Strategy changed to {data.strategy}"
            }
        except Exception as e:
            logger.error(f"Error changing strategy: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def save_custom_instructions(self, request: Request):
        """
        Save custom instructions.
        
        Args:
            request: FastAPI request object.
        
        Returns:
            JSON response with result.
        """
        try:
            # Get data from request
            data = await request.json()
            
            # Validate data
            if not isinstance(data, dict):
                raise ValueError("Invalid data format")
            
            # Save to file
            custom_path = self.proxy_server.config.get("custom_instructions", {}).get("path")
            if not custom_path:
                raise ValueError("Custom instructions path not configured")
            
            # Create directory if it doesn't exist
            custom_file = Path(custom_path)
            custom_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write data
            with open(custom_file, "w") as f:
                json.dump(data, f, indent=2)
            
            # Reload dictionary strategy
            if self.proxy_server.stego_engine.strategy_name == "dictionary":
                self.proxy_server.stego_engine.strategy._load_custom_dictionaries(custom_path)
            
            logger.info(f"Saved custom instructions to {custom_path}")
            
            return {
                "message": "Custom instructions saved successfully"
            }
        except Exception as e:
            logger.error(f"Error saving custom instructions: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

def setup_routes(app, proxy_server):
    """
    Set up the web UI routes.
    
    Args:
        app: FastAPI app.
        proxy_server: Proxy server instance.
    """
    # Create handler
    handler = StegoUIHandler(proxy_server)
    
    # Set up static files
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Set up routes
    # Pages
    app.add_api_route("/", handler.index, methods=["GET"])
    app.add_api_route("/settings", handler.settings, methods=["GET"])
    app.add_api_route("/statistics", handler.statistics, methods=["GET"])
    app.add_api_route("/custom-instructions", handler.custom_instructions, methods=["GET"])
    
    # API endpoints
    app.add_api_route("/api/status", handler.get_status, methods=["GET"])
    app.add_api_route("/api/settings/toggle_compression", handler.toggle_compression, methods=["POST"])
    app.add_api_route("/api/settings/toggle_deep_learning", handler.toggle_deep_learning, methods=["POST"])
    app.add_api_route("/api/settings/change_strategy", handler.change_strategy, methods=["POST"])
    app.add_api_route("/api/custom_instructions", handler.save_custom_instructions, methods=["POST"])
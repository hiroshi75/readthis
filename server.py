#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, TypeVar, Generic, Callable, cast

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolRequestParams, ErrorData
from mcp import McpError

# Custom error code definition
class ErrorCode:
    """Error code definition"""
    # Error codes use integer values
    InvalidRequest = 400  # Invalid request
    InvalidParams = 422   # Invalid parameters
    InternalError = 500   # Internal error

from html_parser import fetch_document, parse_html_content, DocumentFetchError

# Logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format='[%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("readthis-server")


class ReadThisServer:
    """
    ReadThis MCP Server
    
    An MCP server for retrieving and parsing HTML documents
    """
    
    def __init__(self) -> None:
        """Initialize the server"""
        logger.error("[Setup] Initializing ReadThis MCP Server...")
        
        # Adjust Server type
        self.server = Server(
            name="readthis-server", 
            version="0.1.0"
        )
        
        # Load manuals.json
        self.documents_config = self._load_documents_config()
        
        # Register tool handlers
        self._register_tools()
        
        # MCP Server initialization complete log
        logger.error("[Setup] Server object has been initialized")
        
        # Register error handler (ignore type check)
        self.server.onerror = lambda error: logger.error(f"[Error] MCP error: {error}")  # type: ignore
    
    def _load_documents_config(self) -> Dict:
        """
        Load the manuals.json file
        
        Returns:
            Dict: Dictionary of document settings
        """
        try:
            config_path = Path('./manuals.json')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    logger.error(f"[Setup] Loaded manuals.json: {config_path}")
                    return json.load(f)
            else:
                logger.error("[Setup] manuals.json not found. Using default settings.")
                return {"documents": []}
        except Exception as e:
            logger.error(f"[Error] Failed to load manuals.json: {str(e)}")
            return {"documents": []}
    
    def _resolve_url(self, url_or_id: str) -> str:
        """
        Resolve a URL from a URL or ID
        
        Args:
            url_or_id: URL or document ID
            
        Returns:
            str: Resolved URL
            
        Raises:
            ValueError: If the ID is invalid
        """
        # If it's already a URL, return it as is
        if url_or_id.startswith(('http://', 'https://')):
            return url_or_id
        
        # Resolve URL from ID
        for doc in self.documents_config.get("documents", []):
            if doc.get("id") == url_or_id:
                return doc.get("url")
        
        # Error if matching ID is not found
        raise ValueError(f"Invalid document ID: {url_or_id}. Please specify a valid URL or an ID defined in manuals.json.")
    
    def _register_tools(self) -> None:
        """Register tool handlers"""
        logger.error("[Setup] Registering tool handlers...")
        
        # Define handler for readthis tool
        async def handle_readthis_request(request: Any) -> str:
            """
            Retrieve an HTML document from the specified URL and return its content
            
            Args:
                request: Request information (including URL)
                
            Returns:
                str: Content of the retrieved document
            """
            # Get URL from request
            url = request.params.url
            try:
                logger.error(f"[API] Document retrieval request: {url}")
                
                # Resolve URL
                resolved_url = self._resolve_url(url)
                logger.error(f"[API] Resolved URL: {resolved_url}")
                
                # Fetch document
                html_content = fetch_document(resolved_url)
                
                # Parse HTML
                parsed_content = parse_html_content(html_content)
                
                logger.error(f"[API] Document retrieval complete: {len(parsed_content)} characters")
                return parsed_content
                
            except ValueError as e:
                logger.error(f"[Error] Invalid URL/ID: {str(e)}")
                raise McpError(ErrorData(code=ErrorCode.InvalidParams, message=str(e)))
            except DocumentFetchError as e:
                logger.error(f"[Error] Document retrieval error: {str(e)}")
                raise McpError(ErrorData(code=ErrorCode.InternalError, message=f"Failed to retrieve document: {str(e)}"))
            except Exception as e:
                logger.error(f"[Error] Unexpected error: {str(e)}")
                raise McpError(ErrorData(code=ErrorCode.InternalError, message=f"An unexpected error occurred: {str(e)}"))
        
        # Define handler for reload_manuals tool
        async def handle_reload_manuals_request(request: Any) -> Dict:
            """
            Handler to reload the manuals.json file and update document settings
            
            Args:
                request: Request information
                
            Returns:
                Dict: Document settings information after update and result status
            """
            try:
                logger.error("[API] Starting manuals.json reload")
                
                # Record state before reloading configuration file
                previous_count = len(self.documents_config.get("documents", []))
                
                # Reload configuration file
                self.documents_config = self._load_documents_config()
                
                # Get state after update
                current_count = len(self.documents_config.get("documents", []))
                
                # Return result
                result = {
                    "success": True,
                    "message": f"Successfully reloaded manuals.json",
                    "previous_documents_count": previous_count,
                    "current_documents_count": current_count, 
                    "documents": self.documents_config
                }
                
                logger.error(f"[API] manuals.json reload complete: {current_count} document settings")
                return result
                
            except Exception as e:
                logger.error(f"[Error] An error occurred while reloading manuals.json: {str(e)}")
                raise McpError(ErrorData(code=ErrorCode.InternalError, message=f"Failed to reload configuration file: {str(e)}"))
                
        # Register tool handlers (may need to be modified according to actual MCP API)
        # Currently commented out, please implement according to the MCP SDK specifications
        logger.error("[Setup] Please implement tool handler registration according to MCP SDK specifications")
        
        # Example: Register a handler for CallToolRequestParams
        # self.server.tool("readthis", readthis_handler)
        # self.server.tool("reload_manuals", reload_manuals_handler)
    
    async def run(self) -> None:
        """Run the server"""
        transport = stdio_server()
        await self.server.connect(transport)  # type: ignore
        logger.error("[Setup] ReadThis MCP Server started (via stdio)")


if __name__ == "__main__":
    import asyncio
    
    server: ReadThisServer = ReadThisServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.error("[Setup] Shutting down server...")
    except Exception as e:
        logger.error(f"[Error] An error occurred during server execution: {str(e)}")

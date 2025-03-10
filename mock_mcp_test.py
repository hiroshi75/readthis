#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mock test for ReadThis MCP Server

This script simulates the integration with the MCP server using mocks,
and verifies the operation of the readthis tool.
"""

import os
import sys
import json
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add path to the module being tested
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import html_parser
from html_parser import fetch_document, parse_html_content, DocumentFetchError

# For creating server class mock
class MockServer:
    def __init__(self):
        self.tool_handlers = {}
    
    def tool(self, name):
        def decorator(func):
            self.tool_handlers[name] = func
            return func
        return decorator

# Mock the mcp module for testing
class MockMcp:
    @staticmethod
    async def use_tool(server_name, tool_name, args):
        if server_name != "readthis-server" or tool_name != "readthis":
            raise ValueError(f"Unknown tool: {server_name}.{tool_name}")
        
        url = args.get("url")
        if not url:
            raise ValueError("URL is required")
        
        # Return mock response instead of calling actual fetch_document and parse_html_content
        if url.startswith(("http://", "https://")):
            return f"Mock content for {url}"
        else:
            # When resolving URL from ID
            mock_docs = {
                "python-asyncio": "https://docs.python.org/3/library/asyncio.html",
                "react-hooks": "https://react.dev/reference/react"
            }
            resolved_url = mock_docs.get(url)
            if not resolved_url:
                raise ValueError(f"Unknown document ID: {url}")
            return f"Mock content for resolved URL: {resolved_url}"


class TestReadThisMockMcp(unittest.TestCase):
    """Mock test for ReadThis MCP Server"""
    
    def setUp(self):
        """Set up test environment"""
        # Create server mock
        self.mock_server = MockServer()
        
        # Partially reproduce the actual server code
        def resolve_url(url_or_id):
            # If it's already a URL, return it as is
            if url_or_id.startswith(('http://', 'https://')):
                return url_or_id
            
            # Resolve URL from ID
            mock_docs = {
                "python-asyncio": "https://docs.python.org/3/library/asyncio.html",
                "react-hooks": "https://react.dev/reference/react"
            }
            
            resolved_url = mock_docs.get(url_or_id)
            if not resolved_url:
                raise ValueError(f"Invalid document ID: {url_or_id}")
            
            return resolved_url
        
        # Define readthis tool function
        @self.mock_server.tool("readthis")
        async def readthis(url):
            try:
                print(f"[Mock] Document retrieval request: {url}")
                
                # Resolve URL
                resolved_url = resolve_url(url)
                print(f"[Mock] Resolved URL: {resolved_url}")
                
                # Skip actual HTTP retrieval and parsing, return mock response
                return f"Mock content for {resolved_url}"
                
            except ValueError as e:
                print(f"[Mock Error] Invalid URL/ID: {str(e)}")
                raise ValueError(str(e))
            except Exception as e:
                print(f"[Mock Error] Unexpected error: {str(e)}")
                raise Exception(str(e))
    
    @patch('sys.stdout')  # Patch to capture standard output
    def test_readthis_with_url(self, mock_stdout):
        """Test readthis tool using URL"""
        import asyncio
        
        # Test URL
        test_url = "https://example.com/test"
        
        # Execute readthis tool function asynchronously
        result = asyncio.run(self.mock_server.tool_handlers["readthis"](test_url))
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIn("Mock content for", result)
        self.assertIn(test_url, result)
        print(f"[Test] readthis_with_url: success")
    
    @patch('sys.stdout')
    def test_readthis_with_id(self, mock_stdout):
        """Test readthis tool using document ID"""
        import asyncio
        
        # Test ID
        test_id = "python-asyncio"
        expected_url = "https://docs.python.org/3/library/asyncio.html"
        
        # Execute readthis tool function asynchronously
        result = asyncio.run(self.mock_server.tool_handlers["readthis"](test_id))
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIn("Mock content for", result)
        self.assertIn(expected_url, result)
        print(f"[Test] readthis_with_id: success")
    
    @patch('sys.stdout')
    def test_readthis_with_invalid_id(self, mock_stdout):
        """Test readthis tool using invalid ID"""
        import asyncio
        
        # Invalid ID
        invalid_id = "non-existent-id"
        
        # Confirm that an exception is raised
        with self.assertRaises(ValueError):
            asyncio.run(self.mock_server.tool_handlers["readthis"](invalid_id))
        
        print(f"[Test] readthis_with_invalid_id: success")
    
    def test_mock_mcp_use_tool(self):
        """Test use_tool using MockMcp class"""
        import asyncio
        
        # Mock MCP instance
        mock_mcp = MockMcp()
        
        # Test with URL
        result1 = asyncio.run(mock_mcp.use_tool("readthis-server", "readthis", {"url": "https://example.com/test"}))
        self.assertIn("Mock content for", result1)
        
        # Test with ID
        result2 = asyncio.run(mock_mcp.use_tool("readthis-server", "readthis", {"url": "python-asyncio"}))
        self.assertIn("Mock content for resolved URL", result2)
        self.assertIn("asyncio", result2)
        
        # Test with invalid ID
        with self.assertRaises(ValueError):
            asyncio.run(mock_mcp.use_tool("readthis-server", "readthis", {"url": "non-existent-id"}))
        
        print(f"[Test] mock_mcp_use_tool: success")


if __name__ == "__main__":
    print("Starting mock tests for ReadThis MCP Server...")
    unittest.main()

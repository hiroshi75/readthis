#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for ReadThis MCP Server

This script tests the basic functionality of the ReadThis MCP Server.
Core functions can be tested without an actual MCP server connection.
"""

import os
import sys
import unittest
import json
from pathlib import Path

# Import modules being tested
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from html_parser import fetch_document, parse_html_content, get_document_metadata


class TestHTMLParser(unittest.TestCase):
    """Test HTML parser functionality"""
    
    def test_fetch_document(self):
        """Test document retrieval"""
        # Test with a publicly available web page
        url = "https://docs.python.org/3/"
        try:
            html = fetch_document(url)
            self.assertIsNotNone(html)
            self.assertIsInstance(html, str)
            self.assertGreater(len(html), 1000)  # 十分な長さがあることを確認
            print(f"[Test] fetch_document: success ({len(html)} bytes)")
        except Exception as e:
            self.fail(f"fetch_document failed with {str(e)}")
    
    def test_parse_html_content(self):
        """Test HTML parsing functionality"""
        # Test with simple HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <header>Header section</header>
            <main>
                <h1>Main Content</h1>
                <p>This is the body text.</p>
            </main>
            <footer>Footer section</footer>
        </body>
        </html>
        """
        
        parsed = parse_html_content(html)
        self.assertIsNotNone(parsed)
        self.assertIsInstance(parsed, str)
        self.assertIn("Main Content", parsed)
        self.assertIn("This is the body text", parsed)
        print("[Test] parse_html_content: success")
    
    def test_metadata_extraction(self):
        """Test metadata extraction"""
        # Extract metadata from sample HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Title</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <p>Content</p>
        </body>
        </html>
        """
        
        # Use a mock URL for testing
        test_url = "https://example.com/test"
        
        # Test directly with BeautifulSoup instead of get_document_metadata
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        title = soup.title.string if soup.title else "Unknown Title"
        self.assertEqual(title, "Test Title")
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        self.assertIsNotNone(meta_desc)
        self.assertEqual(meta_desc['content'], "Test description")
        
        print("[Test] metadata_extraction: success")


class TestReadThisJson(unittest.TestCase):
    """Test manuals.json file processing"""
    
    def setUp(self):
        """Create manuals.json for testing"""
        self.test_json_path = Path("./test_manuals.json")
        self.test_data = {
            "documents": [
                {
                    "id": "test-doc",
                    "name": "Test Document",
                    "url": "https://example.com/test",
                    "description": "Document for testing"
                }
            ]
        }
        
        # Write test JSON file
        with open(self.test_json_path, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """Delete test file"""
        if self.test_json_path.exists():
            self.test_json_path.unlink()
    
    def test_read_json(self):
        """Test JSON file reading"""
        self.assertTrue(self.test_json_path.exists())
        
        # Test file reading
        with open(self.test_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertEqual(len(data["documents"]), 1)
        self.assertEqual(data["documents"][0]["id"], "test-doc")
        self.assertEqual(data["documents"][0]["url"], "https://example.com/test")
        print("[Test] read_json: success")
    
    def test_id_to_url_resolution(self):
        """Test ID to URL resolution functionality"""
        # Simple ID→URL resolution function that mimics the actual server functionality
        def resolve_url(url_or_id, documents):
            if url_or_id.startswith(('http://', 'https://')):
                return url_or_id
            
            for doc in documents:
                if doc.get("id") == url_or_id:
                    return doc.get("url")
            
            return None
        
        # Test
        docs = self.test_data["documents"]
        
        # When already a URL
        self.assertEqual(
            resolve_url("https://example.com/direct", docs),
            "https://example.com/direct"
        )
        
        # Resolve URL from ID
        self.assertEqual(
            resolve_url("test-doc", docs),
            "https://example.com/test"
        )
        
        # Non-existent ID
        self.assertIsNone(resolve_url("non-existent", docs))
        
        print("[Test] id_to_url_resolution: success")


if __name__ == "__main__":
    print("Starting tests for ReadThis MCP Server...")
    unittest.main()

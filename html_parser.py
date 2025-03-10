#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import trafilatura

# Logging configuration
logger = logging.getLogger("readthis-server")

class DocumentFetchError(Exception):
    """Exception class representing errors during document retrieval"""
    pass


def fetch_document(url: str) -> str:
    """
    Retrieve an HTML document from the specified URL
    
    Args:
        url: URL of the document to retrieve
        
    Returns:
        str: Retrieved HTML document
        
    Raises:
        DocumentFetchError: If document retrieval fails
    """
    try:
        logger.error(f"[Fetch] Retrieving document: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raises exception for HTTP errors
        
        logger.error(f"[Fetch] Document retrieval successful: {len(response.text)} bytes")
        return response.text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[Error] Document retrieval request error: {str(e)}")
        raise DocumentFetchError(f"Failed to retrieve document: {str(e)}")
    except Exception as e:
        logger.error(f"[Error] Unexpected retrieval error: {str(e)}")
        raise DocumentFetchError(f"An unexpected error occurred: {str(e)}")


def parse_html_content(html_content: str) -> str:
    """
    Extract main content from HTML content
    
    Args:
        html_content: HTML content to parse
        
    Returns:
        str: Extracted main content
        
    Raises:
        ValueError: If HTML parsing fails
    """
    try:
        logger.error("[Parse] Parsing HTML content...")
        
        # Extract main content using trafilatura
        extracted_text = trafilatura.extract(html_content, include_links=True, include_images=True, include_tables=True)
        
        # If extraction with trafilatura fails, try simple extraction with BeautifulSoup
        if not extracted_text:
            logger.error("[Parse] Extraction with trafilatura failed, using BeautifulSoup")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove scripts and unnecessary tags
            for script in soup(["script", "style"]):
                script.extract()
                
            # Extract page body
            body = soup.body
            if body:
                # Attempt to remove headers and footers
                for unwanted in body.select('header, footer, nav, .sidebar, #sidebar, .menu, #menu, .navigation, .ads, .advertisement'):
                    unwanted.extract()
                
                # Look for main content
                main_content = body.select_one('main, #main, .main, article, .article, .content, #content')
                if main_content:
                    extracted_text = main_content.get_text(separator='\n')
                else:
                    # If not found, use all text from body
                    extracted_text = body.get_text(separator='\n')
            else:
                # If body is not found
                extracted_text = soup.get_text(separator='\n')
            
            # Clean up extra whitespace and line breaks
            lines = (line.strip() for line in extracted_text.splitlines())
            extracted_text = '\n'.join(line for line in lines if line)
        
        logger.error(f"[Parse] Content extraction complete: {len(extracted_text)} characters")
        return extracted_text
        
    except Exception as e:
        logger.error(f"[Error] HTML parsing error: {str(e)}")
        raise ValueError(f"Failed to parse HTML: {str(e)}")


def get_document_metadata(url: str) -> Dict[str, Any]:
    """
    Get document metadata (title, description, etc.)
    
    Args:
        url: URL of the document to retrieve
        
    Returns:
        Dict[str, Any]: Dictionary of metadata
    """
    try:
        html_content = fetch_document(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        title = soup.title.string if soup.title else "Unknown Title"
        
        # Try to get meta description
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        # Safe access to BeautifulSoup element attributes with type checking
        if meta_desc is not None:
            # Use dictionary-style access with get method to avoid type errors
            attrs = getattr(meta_desc, 'attrs', {})
            description = attrs.get('content', '')  # type: ignore
        
        return {
            "title": title.strip() if title else "",
            "description": description.strip() if description else "",
            "url": url
        }
    except Exception as e:
        logger.error(f"[Error] Metadata retrieval error: {str(e)}")
        return {
            "title": "Retrieval Error",
            "description": "",
            "url": url
        }

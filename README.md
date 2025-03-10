# ReadThis MCP Server

## Background and Motivation

When developing applications with AI agents using modern libraries like LangChain or LangGraph, we often encounter a significant challenge: AI models lack knowledge of the latest APIs and documentation. These libraries evolve rapidly, with new features and API changes that aren't reflected in the AI's training data.

While one solution is to include API documentation in prompts, this approach quickly becomes cumbersome and inefficient. It requires constant manual updates and consumes valuable token space that could be used for more specific instructions.

The ReadThis MCP server was developed to address these limitations. It provides AI agents with direct access to the most current library documentation during software development, allowing them to write more accurate and up-to-date code without requiring extensive prompt engineering.

## Overview

This MCP server is a tool that allows AI agents to access the latest library documentation during software development. It retrieves documentation from the web as specified in the `manuals.json` file placed in the user's project and adds it to the AI's context.

## manuals.json Format

Place a `manuals.json` file in the root directory of your project. This file should describe the documentation information in the following format:

```json
{
  "documents": [
    {
      "id": "react-hooks",
      "name": "React Hooks API",
      "url": "https://reactjs.org/docs/hooks-reference.html",
      "description": "Official React Hooks documentation. Reference when using hooks like useState, useEffect, etc."
    },
    {
      "id": "python-asyncio",
      "url": "https://docs.python.org/3/library/asyncio.html",
      "name": "Python AsyncIO",
      "description": "Python's asynchronous programming library. Reference when developing asynchronous applications."
    }
  ]
}
```

## API: readthis

```python
def readthis(url: str) -> str:
    """
    Retrieves an HTML document from the specified URL and returns its content.
    
    This API is used to fetch documentation for libraries and frameworks that
    AI agents should reference when performing programming tasks.
    The content of the retrieved document is added to the AI agent's context
    to support more accurate program development.
    
    Args:
        url (str): The URL of the document to retrieve
                  Note: You can also use an ID defined in manuals.json
    
    Returns:
        str: The content of the retrieved document (HTML)
             Returns the main content extracted from the HTML
    
    Raises:
        ValueError: If the URL is invalid or an undefined ID is specified in manuals.json
        ConnectionError: If the document retrieval fails
        ParseError: If HTML parsing fails
    
    Examples:
        # Directly specify a URL
        content = readthis("https://docs.python.org/3/library/asyncio.html")
        
        # Use an ID defined in manuals.json
        content = readthis("python-asyncio")
    """
```

## API: reload_manuals

```python
def reload_manuals() -> dict:
    """
    Reloads the manuals.json file to update document settings.
    
    When the manuals.json file is updated while the server is running,
    calling this API will reflect the changes in real-time.
    Server restart is not required.
    
    Returns:
        dict: A dictionary containing the update results
            {
                "success": bool,  # Whether the operation was successful
                "message": str,   # Result message
                "previous_documents_count": int,  # Number of documents before the update
                "current_documents_count": int,   # Number of documents after the update
                "documents": dict  # The entire document configuration after the update
            }
    
    Raises:
        Exception: If there is a failure in loading or parsing the configuration file
    
    Examples:
        # Reload the configuration file
        result = reload_manuals()
        print(f"Reload result: {result['message']}")
        print(f"Document count: {result['current_documents_count']}")
    """
```

## Usage Example

```python
# Using the MCP server's tool
from mcp import use_tool

# Retrieve a document by directly specifying the URL
react_docs = use_tool("readthis-server", "readthis", {"url": "https://reactjs.org/docs/hooks-reference.html"})
print(f"React Hooks documentation: Retrieved {len(react_docs)} characters")

# Using an ID defined in manuals.json
asyncio_docs = use_tool("readthis-server", "readthis", {"url": "python-asyncio"})
print(f"AsyncIO documentation: Retrieved {len(asyncio_docs)} characters")

# Reload manuals.json
reload_result = use_tool("readthis-server", "reload_manuals", {})
print(f"Reload result: {reload_result['message']}")
print(f"Document count: {reload_result['current_documents_count']} (before update: {reload_result['previous_documents_count']})")
```

## Implementation Details

This MCP server performs the following processes:

1. When a URL or ID is specified, it retrieves the corresponding document from the web
2. Extracts the main content from the HTML (removing unnecessary headers, footers, sidebars, etc.)
3. Returns the extracted content as a string
4. Provides a manuals.json reload functionality that updates settings without requiring server restart

## Limitations

- Currently only supports HTML format documents
- Cannot retrieve documents from sites that require authentication
- The accuracy of content extraction may vary depending on the HTML structure of some sites

# ReadThis MCP Server

## Background and Motivation

When developing applications with AI agents using modern libraries like LangChain or LangGraph, we often encounter a significant challenge: AI models lack knowledge of the latest APIs and documentation. These libraries evolve rapidly, with new features and API changes that aren't reflected in the AI's training data.

While one solution is to include API documentation in prompts, this approach quickly becomes cumbersome and inefficient. It requires constant manual updates and consumes valuable token space that could be used for more specific instructions.

The ReadThis MCP server was developed to address these limitations. It provides AI agents with direct access to the most current library documentation during software development, allowing them to write more accurate and up-to-date code without requiring extensive prompt engineering.

## Overview

This MCP server is a tool that allows AI agents to access the latest library documentation during software development. It retrieves documentation from the web as specified in the `manuals.json` file placed in your project and adds it to the AI's context.

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

## Using with Cline

Unlike traditional MCP usage that requires direct API calls in code, ReadThis is designed to work seamlessly with Cline through natural language interactions.

### Usage Method 1: Request Documentation in Prompts

You can ask Cline to use specific documentation when implementing features by mentioning the technology in your prompt. Reference the ID or name defined in your `manuals.json` file:

```
Using React Hooks, please implement a counter component with increment/decrement buttons.
```

or 

```
Please implement an asynchronous file processing utility using Python AsyncIO.
```

When you reference a technology defined in your manuals.json, Cline will automatically retrieve the relevant documentation and use it as context to provide more accurate and up-to-date implementations.

### Usage Method 2: Reload Manuals During Development

If you modify your `manuals.json` file during development (for example, adding new documentation sources), you can ask Cline to reload the manuals with a simple request:

```
Please reload the manuals.
```

Cline will refresh its documentation references without requiring a server restart, allowing you to seamlessly add or update documentation sources during your development session.

## Implementation Details

This MCP server performs the following processes:

1. When a technology is referenced in your prompt, it retrieves the corresponding document from the web
2. Extracts the main content from the HTML (removing unnecessary headers, footers, sidebars, etc.)
3. Uses the extracted content as context for generating code and explanations
4. Provides a manuals.json reload functionality that updates settings without requiring server restart

## Limitations

- Currently only supports HTML format documents
- Cannot retrieve documents from sites that require authentication
- The accuracy of content extraction may vary depending on the HTML structure of some sites
- Excessively large manual pages may exceed prompt length limitations and are not suitable for this approach

# Installation Instructions for ReadThis MCP Plugin

This document explains how to install and configure the ReadThis MCP plugin.

## Prerequisites

- Python 3.12 or higher
- uv (for package installation)
- Claude desktop app with Cline extension installed

## Installation Steps

1. Clone or download the repository.

```bash
git clone <repository-url>
cd readthis
```

2. Install uv.

```bash
# Linux, MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Install dependencies.

```bash
uv venv
```

## MCP Server Configuration

1. Open the Claude desktop app configuration file.

Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

macOS:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

2. Add the following MCP server definition to the configuration file.

```json
{
  "mcpServers": {
    "readthis-server": {
      "command": "uv",
      "args": ["run", "--", "python", "path/to/readthis/server.py"],
      "env": {
        "PWD": "path/to/readthis/"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Replace `path/to/readthis/server.py` with the actual path to the server.py file.

## How to Use

1. Create a `manuals.json` file in the root directory of your project and define the documents you want to reference.

```json
{
  "documents": [
    {
      "id": "react-hooks",
      "name": "React Hooks API",
      "url": "https://react.dev/reference/react",
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

2. Ask Claude to read the documentation.

Example:
```
I'm developing with React hooks. Please reference the documentation and explain how to use useState and useEffect.
```

Claude will use the ReadThis MCP server to access the specified documents as needed to respond.

## Troubleshooting

- If the MCP server is not connected, verify that the path in the Claude configuration file is correct.
- If the document cannot be retrieved, check that the URL is correct and that internet connection is available.
- To check logs, run server.py directly and review the output.

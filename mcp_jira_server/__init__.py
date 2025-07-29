"""mcp_jira_server package.

Contains a read-only MCP server exposing JIRA search and issue retrieval tools.
"""

__all__ = [
    "create_server",
]

from .server import create_server

# EOF

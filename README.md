# MCP JIRA Server

![PR Check](https://github.com/jewzaam/mcp-jira-server/workflows/PR%20Check/badge.svg)
![Coverage Check](https://github.com/jewzaam/mcp-jira-server/workflows/Coverage%20Check/badge.svg)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/jewzaam/mcp-jira-server/main/.github/badges/coverage.json)](https://github.com/jewzaam/mcp-jira-server/actions/workflows/coverage-badge.yml)

A read-only Model Context Protocol (MCP) server that provides AI assistants with tools to search and retrieve JIRA issues. This server integrates with AI tools like Claude Desktop, VS Code, and other MCP-compatible clients.

## Features

- **Search JIRA Issues**: Support for both JQL queries and simple text searches
- **Retrieve Issue Details**: Get comprehensive information about specific JIRA issues  
- **Flexible Authentication**: Support for username/password, API tokens, and Personal Access Tokens
- **Configuration Management**: YAML/JSON configuration files with environment variable support
- **Read-Only Operations**: Safe integration with AI tools - no data modification capabilities

## Setup

### Prerequisites
- Python 3.8 or higher
- Access to a JIRA instance with valid credentials
- MCP-compatible client (Claude Desktop, VS Code with MCP extension, etc.)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/jewzaam/mcp-jira-server.git
   cd mcp-jira-server
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Configuration File

Create a configuration file (YAML or JSON) with your JIRA connection details:

```yaml
# mcp_jira_server.yaml
url: https://your-jira-instance.com
username: your-username
token: your-api-token  # Recommended over password
```

Or using JSON:
```json
{
  "url": "https://your-jira-instance.com",
  "username": "your-username",
  "bearer_token": "your-personal-access-token"
}
```

### Authentication Methods

The server supports multiple authentication methods:

1. **API Token (Recommended)**:
   ```yaml
   url: https://your-jira-instance.com
   username: your-username
   token: your-api-token
   ```

2. **Personal Access Token**:
   ```yaml
   url: https://your-jira-instance.com
   bearer_token: your-personal-access-token
   ```

3. **Username/Password**:
   ```yaml
   url: https://your-jira-instance.com
   username: your-username
   password: your-password
   ```

### Configuration File Locations

The server looks for configuration files in this order:
1. Explicit path via `--config` argument
2. Path specified in `MCP_JIRA_CONFIG` environment variable
3. `mcp_jira_server.yaml` in the current directory

## Usage

### Running the Server

Start the MCP server using the command line:

```bash
# Using configuration file
python -m mcp_jira_server.server

# With explicit configuration path
python -m mcp_jira_server.server --config /path/to/config.yaml

# Override config with command line arguments
python -m mcp_jira_server.server --url https://jira.company.com --username myuser --token mytoken
```

### Command Line Options

```
Options:
  -c, --config TEXT      Path to YAML/JSON configuration file
  --url TEXT            JIRA base URL (overrides config)
  --username TEXT       JIRA username (overrides config)
  --password TEXT       JIRA password (overrides config)
  --token TEXT          JIRA API token (overrides config)
  --bearer-token TEXT   Personal Access Token (overrides config)
  --help               Show help message
```

### MCP Client Integration

#### Claude Desktop

Add the server to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": [
        "/path/to/mcp-jira-server/mcp_jira_server/server.py",
        "--config",
        "/path/to/your/config.yaml"
      ]
    }
  }
}
```

#### VS Code with MCP Extension

Configure the server in your VS Code MCP settings:

```json
{
  "mcp.servers": {
    "jira": {
      "command": "python",
      "args": ["-m", "mcp_jira_server.server"],
      "cwd": "/path/to/mcp-jira-server"
    }
  }
}
```

## Available Tools

The server provides seven MCP tools:

### Basic Tools

#### 1. `search_issues`
Search for JIRA issues using JQL or simple text queries.

**Parameters:**
- `query` (string): JQL query or simple search term
- `max_results` (int, optional): Maximum number of results (1-100, default 25)

**Examples:**
- Simple text: `"bug in authentication"`
- JQL query: `"project = PROJ AND status = Open"`

#### 2. `get_issue` 
Retrieve detailed information about a specific JIRA issue.

**Parameters:**
- `key` (string): JIRA issue key (e.g., "PROJ-123")
- `expand` (string, optional): Comma-separated fields to expand

**Example:**
- Get issue: `"PROJ-123"`
- With expansion: `"PROJ-123"` with expand `"changelog,comments"`

#### 3. `identifier_hint`
Get help about JIRA issue identifier format.

**Parameters:** None

**Returns:** Description of valid JIRA issue key patterns.

### Relationship Discovery Tools

#### 4. `get_issue_relationships`
Get comprehensive relationship information for a specific JIRA issue.

**Parameters:**
- `issue_key` (string): JIRA issue key (e.g., "PROJ-123")

**Returns:** Complete relationship data including:
- Parent issue (for subtasks)
- List of subtask keys
- Issue links with type and direction
- Count of remote links

#### 5. `get_descendants`
Get all descendants of an issue based on relationship types and traversal depth.

**Parameters:**
- `issue_key` (string): Root JIRA issue key
- `max_depth` (int, optional): Maximum traversal depth (-1 for unlimited, default: 3)
- `include_subtasks` (bool, optional): Include subtask relationships (default: true)
- `include_links` (bool, optional): Include issue links (default: true)
- `include_parent_links` (bool, optional): Include custom parent-link fields (default: false)

**Returns:** Tree structure with all descendant issues and traversal metadata.

#### 6. `get_children`
Get direct children of an issue (subtasks and optionally parent-link children).

**Parameters:**
- `issue_key` (string): Parent JIRA issue key
- `include_parent_links` (bool, optional): Include custom parent-link children (default: false)
- `parent_link_field` (string, optional): Name of parent link field (default: "Parent Link")

**Returns:** List of immediate child issues.

#### 7. `get_linked_issues`
Get issues linked to the specified issue via JIRA issue links.

**Parameters:**
- `issue_key` (string): JIRA issue key
- `link_type` (string, optional): Filter by specific link type (case-insensitive)

**Returns:** List of linked issues with link type, direction, and relationship details.

#### 8. `get_parent`
Get the immediate parent of a JIRA issue.

**Parameters:**
- `issue_key` (string): JIRA issue key
- `include_parent_links` (boolean, optional): Include custom parent link fields (default: true)
- `parent_link_field` (string, optional): Name of parent link field (default: "Parent Link")

**Returns:** Parent information including parent key, summary, and relationship type.

**Example:**
```
get_parent("PROJ-123")
# Returns: ParentInfo with parent_key, parent_summary, parent_type
```

#### 9. `get_ancestors`
Get all ancestors of a JIRA issue by following parent relationships recursively.

**Parameters:**
- `issue_key` (string): JIRA issue key  
- `max_depth` (int, optional): Maximum traversal depth (-1 for unlimited, default: 5)
- `include_parent_links` (boolean, optional): Include custom parent link fields (default: true)
- `parent_link_field` (string, optional): Name of parent link field (default: "Parent Link")

**Returns:** Tree structure with all ancestor issues, traversal order, and metadata.

**Example:**
```
get_ancestors("PROJ-123", max_depth=3)
# Returns: AncestorTree with ancestors list, traversal_order, and metadata
```

## Development

### Running Tests

The project includes comprehensive unit tests:

```bash
# Run all tests
python -m unittest discover mcp_jira_server/

# Run specific test modules
python -m unittest mcp_jira_server.test_config
python -m unittest mcp_jira_server.test_server

# Run with verbose output
python -m unittest mcp_jira_server.test_server -v
```

### Test Coverage

Run tests with coverage reporting:

```bash
# Install coverage if not already installed
pip install -r requirements-test.txt

# Run tests with coverage
coverage run --source=mcp_jira_server -m unittest discover mcp_jira_server/
coverage report -m
coverage html  # Generate HTML report
```

### Code Quality

The project maintains high code quality standards:

```bash
# Run linting
flake8 mcp_jira_server/ --max-line-length=100

# Check for common issues
python -m py_compile mcp_jira_server/*.py
```

## Security Considerations

- **API Tokens**: Always prefer API tokens over passwords for authentication
- **Configuration Files**: Ensure configuration files with credentials have restricted permissions (`chmod 600`)
- **Environment Variables**: Consider using environment variables for sensitive data
- **HTTPS**: Always use HTTPS URLs for JIRA connections
- **Read-Only**: The server only provides read access to JIRA data

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify your credentials are correct
   - Check if your JIRA instance requires specific authentication methods
   - Ensure your user has appropriate permissions

2. **Connection Issues**:
   - Verify the JIRA URL is correct and accessible
   - Check network connectivity and firewall settings
   - Confirm JIRA instance is running and responsive

3. **MCP Integration Issues**:
   - Verify the server starts correctly from command line
   - Check MCP client configuration syntax
   - Review client logs for connection errors

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When contributing to this project:

1. Ensure all tests pass: `python -m unittest discover`
2. Maintain or improve test coverage
3. Follow existing code style and patterns
4. Add tests for new functionality
5. Update documentation as needed

## License

This program is licensed under GPL-3.0-or-later. See the LICENSE file for details.

## Attribution

Generated by: Cursor (Claude) 
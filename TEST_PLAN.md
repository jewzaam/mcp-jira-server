# MCP JIRA Server Test Plan

This document maps 1:1 to unit tests in the codebase. Each test item corresponds to a specific test method for the MCP JIRA server.  Validation is done by a human, checking that implementation meets intent of the test, not just technically the literal interpretation of the description.

## CONFIG - Configuration Management

| Test ID | Description | Validated |
|---------|-------------|-----------|
| CONFIG-01 | Load configuration from explicit path | ✅ |
| CONFIG-02 | Load configuration from environment variable | ✅ |
| CONFIG-03 | Load configuration from default file | ✅ |
| CONFIG-04 | Handle missing configuration file gracefully | ✅ |
| CONFIG-05 | Parse YAML configuration correctly | ✅ |
| CONFIG-06 | Parse JSON configuration correctly | ✅ |
| CONFIG-07 | Handle invalid YAML configuration | ✅ |
| CONFIG-08 | Handle invalid JSON configuration | ✅ |
| CONFIG-09 | Configuration priority order (explicit > env > default) | ✅ |
| CONFIG-10 | Configuration priority order (env > default) | ✅ |
| CONFIG-11 | Configuration priority order (default) | ✅ |

## TOOLS - MCP Tool Implementation

| Test ID | Description | Validated |
|---------|-------------|-----------|
| TOOLS-01 | Search issues with simple text query | |
| TOOLS-02 | Search issues with JQL query | |
| TOOLS-03 | Search issues with JQL detection (equals sign) | |
| TOOLS-04 | Search issues with JQL detection (AND/OR operators) | |
| TOOLS-05 | Search issues with max results parameter | |
| TOOLS-06 | Search issues with max results boundary (1-100) | |
| TOOLS-07 | Search issues returns proper IssueSummary objects | |
| TOOLS-08 | Get single issue by key | |
| TOOLS-09 | Get issue with expand parameter | |
| TOOLS-10 | Get issue returns proper IssueDetails object | |
| TOOLS-11 | Identifier hint returns expected format description | |
| TOOLS-12 | Get issue relationships with all relationship types | |
| TOOLS-13 | Get issue relationships with no relationships | |
| TOOLS-14 | Get issue relationships link parsing | |
| TOOLS-15 | Get descendants basic functionality | |
| TOOLS-16 | Get descendants excludes root issue from results | |
| TOOLS-17 | Get descendants with custom parameters | |
| TOOLS-18 | Get children with subtasks only | |
| TOOLS-19 | Get children with parent links enabled | |
| TOOLS-20 | Get children handles parent link fetch errors gracefully | |
| TOOLS-21 | Get linked issues returns all links | |
| TOOLS-22 | Get linked issues with link type filter | |
| TOOLS-23 | Get linked issues with case-insensitive filter | |
| TOOLS-24 | Get linked issues with no matching links | |
| TOOLS-25 | Get linked issues handles missing or malformed link data | |
| TOOLS-26 | Get parent with subtask parent relationship | |
| TOOLS-27 | Get parent with no parent relationship | |
| TOOLS-28 | Get parent with custom parent link field | |
| TOOLS-29 | Get parent with parent link field containing value | |
| TOOLS-30 | Get ancestors with single level hierarchy | |
| TOOLS-31 | Get ancestors with multi-level hierarchy | |
| TOOLS-32 | Get ancestors with depth limit | |
| TOOLS-33 | Get ancestors for issue with no parents | |
| TOOLS-34 | Get ancestors handles parent fetch errors gracefully | |
| TOOLS-35 | Get ancestors prevents infinite loops from cycles | |

## SERVER - MCP Server Creation and Configuration

| Test ID | Description | Validated |
|---------|-------------|-----------|
| SERVER-01 | Create server with URL only | |
| SERVER-02 | Create server with username/password auth | |
| SERVER-03 | Create server with username/token auth | |
| SERVER-04 | Create server with bearer token auth | |
| SERVER-05 | Server has correct name and instructions | |
| SERVER-06 | Server registers all nine tools | |
| SERVER-07 | Tools have correct annotations (read-only, idempotent) | |

## CLI - Command Line Interface

| Test ID | Description | Validated |
|---------|-------------|-----------|
| CLI-01 | Parse arguments with config file option | |
| CLI-02 | Parse arguments with all authentication options | |
| CLI-03 | Parse arguments with required URL parameter | |
| CLI-04 | Handle missing URL requirement | |
| CLI-05 | CLI arguments override config file values | |
| CLI-06 | Config loading with explicit path | |
| CLI-07 | Config loading with environment variable | |
| CLI-08 | Config loading with default file fallback | |

## MODELS - Data Model Validation

| Test ID | Description | Validated |
|---------|-------------|-----------|
| MODELS-01 | IssueSummary model validation | |
| MODELS-02 | IssueSummary model with all required fields | |
| MODELS-03 | IssueSummary model ignores extra fields | |
| MODELS-04 | IssueDetails model validation | |
| MODELS-05 | IssueDetails model with optional description | |
| MODELS-06 | IssueDetails model with None description | |
| MODELS-07 | IssueDetails model includes raw field | |

## INTEGRATION - Component Integration

| Test ID | Description | Validated |
|---------|-------------|-----------|
| INTEGRATION-01 | JiraTools initialization with client | |
| INTEGRATION-02 | Search tool integration with JiraClient | |
| INTEGRATION-03 | Get issue tool integration with JiraClient | |
| INTEGRATION-04 | Tool error handling for authentication failures | |
| INTEGRATION-05 | Tool error handling for network errors | |
| INTEGRATION-06 | Tool error handling for API errors | |

## AUTH - Authentication Integration

| Test ID | Description | Validated |
|---------|-------------|-----------|
| AUTH-01 | Server creation with basic auth (username/password) | |
| AUTH-02 | Server creation with token auth (username/token) | |
| AUTH-03 | Server creation with bearer token auth | |
| AUTH-04 | Server creation without authentication | |
| AUTH-05 | Config file authentication parameters | |
| AUTH-06 | CLI authentication parameter override | |

## ERROR - Error Handling

| Test ID | Description | Validated |
|---------|-------------|-----------|
| ERROR-01 | Handle JiraClient exceptions in search | |
| ERROR-02 | Handle JiraClient exceptions in get_issue | |
| ERROR-03 | Handle malformed configuration files | |
| ERROR-04 | Handle missing required configuration | |
| ERROR-05 | Handle invalid issue keys | |
| ERROR-06 | Handle network timeouts | |
| ERROR-07 | Handle HTTP error responses | |

## ASYNC - Asynchronous Operations

| Test ID | Description | Validated |
|---------|-------------|-----------|
| ASYNC-01 | Async search_issues method | |
| ASYNC-02 | Async get_issue method | |
| ASYNC-03 | Async identifier_hint method | |
| ASYNC-04 | Async main function entry point | |
| ASYNC-05 | Server startup and shutdown | |

## Usage Notes

1. Each test ID maps directly to a test method in the corresponding test file
2. Use the test ID to quickly locate and modify specific tests  
3. When adding new functionality, add corresponding test entries to the appropriate feature area
4. Features represent logical groupings that may span multiple source files
5. All tests should mock external dependencies (JIRA API calls) for isolation
6. Integration tests may use real JIRA connections but should be clearly separated 

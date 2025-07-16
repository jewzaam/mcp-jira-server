# JIRA Extractor Test Plan

This document maps 1:1 to unit tests in the codebase. Each test item corresponds to a specific test method.

## LOGGING - Logging Configuration

| Test ID | Description |
|---------|-------------|
| LOGGING-01 | Verify logging setup with INFO level |
| LOGGING-02 | Verify logging setup with DEBUG level |
| LOGGING-03 | Debug information logging |

## URL - URL Processing

| Test ID | Description |
|---------|-------------|
| URL-01 | URL validation with existing scheme |
| URL-02 | URL validation adds https scheme |
| URL-03 | URL validation with invalid URL |
| URL-04 | URL normalization during initialization |

## AUTH - Authentication & Credentials

| Test ID | Description |
|---------|-------------|
| AUTH-01 | Parser with bearer token authentication |
| AUTH-02 | Parser with API token authentication |
| AUTH-03 | Parser with password authentication |
| AUTH-04 | Main function with successful bearer auth |
| AUTH-05 | Token auth with missing username |
| AUTH-06 | No authentication for public issue |
| AUTH-07 | Main function with successful token auth |
| AUTH-08 | Basic auth with password prompt |
| AUTH-09 | Basic auth with missing username |
| AUTH-10 | Client initialization with basic auth |
| AUTH-11 | Client initialization with API token auth |
| AUTH-12 | Client initialization with Bearer token auth |
| AUTH-13 | Client initialization without authentication |
| AUTH-14 | Basic auth with missing credentials |
| AUTH-15 | Token auth with missing credentials |
| AUTH-16 | Issue retrieval with 401 auth error |
| AUTH-17 | Issue retrieval with 403 access denied |
| AUTH-18 | Successful connection test |
| AUTH-19 | Connection test with authentication failure |

## OUTPUT - Output Management

| Test ID | Description |
|---------|-------------|
| OUTPUT-01 | Write output to stdout with "-" |
| OUTPUT-02 | Write output to stdout explicitly |
| OUTPUT-03 | Verify metadata file content generation |
| OUTPUT-04 | Write output to new file |
| OUTPUT-05 | File exists without overwrite flag |
| OUTPUT-06 | File exists with overwrite flag |
| OUTPUT-07 | Write multiple issues to stdout |
| OUTPUT-08 | Write multiple issues to explicit stdout |
| OUTPUT-09 | Write multiple issues to directory |
| OUTPUT-10 | File exists without overwrite |
| OUTPUT-11 | File exists with overwrite enabled |

## PARSING - Command Line Processing

| Test ID | Description |
|---------|-------------|
| PARSING-01 | Parser with required arguments |
| PARSING-02 | Parser with missing required URL |
| PARSING-03 | Parser with missing required issue |
| PARSING-04 | Parser with output options |
| PARSING-05 | Parser with field expansion options |
| PARSING-06 | Parser with debug option |
| PARSING-07 | Parser with descendant depth option |
| PARSING-08 | Parser with short desc-depth option |
| PARSING-09 | Parser with relationship traversal options |
| PARSING-10 | Parser defaults for descendant options |

## EXECUTION - Main Execution Flow

| Test ID | Description |
|---------|-------------|
| EXECUTION-01 | Main function with invalid URL |
| EXECUTION-02 | Main function with connection error |
| EXECUTION-03 | Main function with timeout error |
| EXECUTION-04 | Main function with HTTP error |
| EXECUTION-05 | Generic error with debug enabled |
| EXECUTION-06 | Generic error with debug disabled |
| EXECUTION-07 | Successful execution with directory output |

## DESCENDANT - Descendant Extraction

| Test ID | Description |
|---------|-------------|
| DESCENDANT-01 | Parse depth with valid integer strings |
| DESCENDANT-02 | Parse depth with 'all' keyword |
| DESCENDANT-03 | Parse depth with invalid values |
| DESCENDANT-04 | Descendant extraction including subtasks |
| DESCENDANT-05 | Unlimited depth descendant extraction |
| DESCENDANT-06 | No issues extracted scenario |
| DESCENDANT-07 | Single issue mode fallback |
| DESCENDANT-08 | Invalid depth parameter handling |
| DESCENDANT-09 | Descendants with depth 0 (single issue) |
| DESCENDANT-10 | Descendants with subtasks traversal |
| DESCENDANT-11 | Descendants with issue links traversal |
| DESCENDANT-12 | Descendants with remote links included |
| DESCENDANT-13 | Descendants with unlimited depth (-1) |
| DESCENDANT-14 | Descendants continues when one issue fails |
| DESCENDANT-15 | Descendants with circular references |

## FIELD-MGMT - Field Management

| Test ID | Description |
|---------|-------------|
| FIELD-MGMT-01 | Successful field lookup by name |
| FIELD-MGMT-02 | Field lookup when field doesn't exist |
| FIELD-MGMT-03 | Field lookup results caching |
| FIELD-MGMT-04 | Field lookup with API error |
| FIELD-MGMT-05 | Successful parent link children lookup |
| FIELD-MGMT-06 | Parent link children with no results |
| FIELD-MGMT-07 | Parent link children with error |
| FIELD-MGMT-08 | Related issue keys with parent links |
| FIELD-MGMT-09 | Parent links when field not found |
| FIELD-MGMT-10 | Parent links with children lookup error |

## ISSUE-RETRIEVAL - Issue Data Access

| Test ID | Description |
|---------|-------------|
| ISSUE-RETRIEVAL-01 | Successful issue retrieval |
| ISSUE-RETRIEVAL-02 | Issue retrieval with expand parameter |
| ISSUE-RETRIEVAL-03 | Issue retrieval with 404 not found |
| ISSUE-RETRIEVAL-04 | Issue retrieval with general HTTP error |
| ISSUE-RETRIEVAL-05 | Successful remote links retrieval |
| ISSUE-RETRIEVAL-06 | Remote links with 404 returns empty |
| ISSUE-RETRIEVAL-07 | Remote links with 403 access denied |

## RELATIONSHIPS - Issue Relationships

| Test ID | Description |
|---------|-------------|
| RELATIONSHIPS-01 | Remote links error handling |
| RELATIONSHIPS-02 | Related issue keys from subtask relationships |
| RELATIONSHIPS-03 | Related issue keys from issue links |
| RELATIONSHIPS-04 | Related issue keys processing remote links |
| RELATIONSHIPS-05 | Related issue keys with no relationships |
| RELATIONSHIPS-06 | Descendants with parent links integration |

## Test Statistics

- **Total Tests**: 67
- **Features**: 10 functional areas
- **Coverage**: Authentication (19), Output (11), Descendant (15), Parsing (10), Field Management (10), Issue Retrieval (7), Relationships (6), Execution (7), URL (4), Logging (3)

## Usage Notes

1. Each test ID maps directly to a test method in the corresponding test file
2. Use the test ID to quickly locate and modify specific tests
3. When adding new functionality, add corresponding test entries to the appropriate feature area
4. Features represent logical groupings that may span multiple source files 
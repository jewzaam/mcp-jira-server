# Unit Test Plan: MCP JIRA Server

This document maps 1:1 to unit tests in the codebase based on the requirements in REQUIREMENTS.md. Each test item corresponds to a specific test method for the MCP JIRA server. Tests are organized by MCP tool functionality with supporting sections for configuration and general behaviors. Validation is done by a human, checking that implementation meets intent of the test, not just technically the literal interpretation of the description.

## CONFIG - Configuration Management (CF1)

| Test ID | Description | Validated |
|---------|-------------|-----------|
| CONFIG-01 | Load configuration file with valid YAML structure | |
| CONFIG-02 | Environment variable substitution with ${VAR_NAME} syntax | |
| CONFIG-03 | Support bearer_token authentication type | |
| CONFIG-04 | Support basic_auth authentication type | |
| CONFIG-05 | Support username_password authentication type | |
| CONFIG-06 | Pre-cache field metadata for configured projects at startup | |
| CONFIG-07 | Handle invalid sample issues with startup warnings (don't prevent start) | |
| CONFIG-08 | Fail startup with specific error for missing required configuration | |
| CONFIG-09 | Fail startup with connectivity error for invalid JIRA base URL | |
| CONFIG-10 | Fail startup with auth error for authentication failure | |
| CONFIG-11 | Fail startup with parsing error for malformed YAML | |
| CONFIG-12 | Never log or expose authentication credentials | |

## SEARCH_ISSUES - Issue Search and Discovery

| Test ID | Description | Validated |
|---------|-------------|-----------|
| SEARCH-01 | Simple text query searches issue summaries | |
| SEARCH-02 | JQL detection with equals sign (=) | |
| SEARCH-03 | JQL detection with AND operator | |
| SEARCH-04 | JQL detection with OR operator | |
| SEARCH-05 | JQL detection with "order by" clause | |
| SEARCH-06 | Return page 0 with first 25 issues (default parameters) | |
| SEARCH-07 | Return page 1 with next 5 issues | |
| SEARCH-08 | has_more: true when more pages available | |
| SEARCH-09 | current_page matches requested start_page | |
| SEARCH-10 | total_count accurately reflects total matching issues | |
| SEARCH-11 | Empty result with total_count: 0 and has_more: false | |
| SEARCH-12 | Fail with specific syntax error for invalid JQL | |
| SEARCH-13 | Fail with authentication error | |
| SEARCH-14 | Fail with timeout error for network timeout | |

## GET_ISSUE - Issue Retrieval

| Test ID | Description | Validated |
|---------|-------------|-----------|
| GET_ISSUE-01 | Return complete issue data with all standard fields | |
| GET_ISSUE-02 | Support field selection (key,summary,status,assignee) | |
| GET_ISSUE-03 | Include parent relationship fields in raw field | |
| GET_ISSUE-04 | Consolidate parent fields into single parent_key response field | |
| GET_ISSUE-05 | Raw field contains complete JIRA API response | |
| GET_ISSUE-06 | Fail with "Issue not found" error for non-existent key | |
| GET_ISSUE-07 | Fail with permission error when user lacks access | |
| GET_ISSUE-08 | Fail with format validation error for invalid issue key format | |

## GET_FIELD_METADATA - Field Metadata Discovery

| Test ID | Description | Validated |
|---------|-------------|-----------|
| FIELD_META-01 | Return cached metadata for pre-configured project (RFE) | |
| FIELD_META-02 | Discover and cache metadata using sample issue | |
| FIELD_META-03 | Fail when no sample_issue provided and no cached data exists | |
| FIELD_META-04 | Mark fields matching .*Link pattern as used_for_parent_key: true | |
| FIELD_META-05 | Mark non-link fields as used_for_parent_key: false | |
| FIELD_META-06 | Include field type, description, and requirement status | |
| FIELD_META-07 | Use editmeta API for field discovery | |
| FIELD_META-08 | Cache discovered metadata for future use | |
| FIELD_META-09 | Fail with "Project not found" error for non-existent project | |
| FIELD_META-10 | Fail with "Sample issue not found" error for non-existent sample | |
| FIELD_META-11 | Fail with permission error for insufficient editmeta access | |

## GET_CHILDREN - Immediate Child Discovery

| Test ID | Description | Validated |
|---------|-------------|-----------|
| CHILDREN-01 | Return page 0 with first 100 direct child issues (defaults) | |
| CHILDREN-02 | Return page 0 with 5 results (custom max_results) | |
| CHILDREN-03 | Return page 1 with 5 results (pagination) | |
| CHILDREN-04 | Field selection returns only specified fields | |
| CHILDREN-05 | Order results by specified field (created) | |
| CHILDREN-06 | Combined field selection and ordering | |
| CHILDREN-07 | Empty result with total_count: 0 for issues with no children | |
| CHILDREN-08 | Include all standard fields plus parent relationship fields (default) | |
| CHILDREN-09 | Efficient (single) JQL queries for parent-link discovery | |
| CHILDREN-10 | Fail with "Issue not found" error for non-existent issue | |
| CHILDREN-11 | Fail with rate limit error after retries | |

## GET_DESCENDANTS - Hierarchy Descendant Discovery

| Test ID | Description | Validated |
|---------|-------------|-----------|
| DESCENDANTS-01 | Single API call using childIssuesOf() JQL function | |
| DESCENDANTS-02 | Search root issue NOT included in results | |
| DESCENDANTS-03 | Every descendant has parent_key field populated | |
| DESCENDANTS-04 | All descendants form connected hierarchy tree | |
| DESCENDANTS-05 | Default field selection includes parent_key for reconstruction | |
| DESCENDANTS-06 | Explicit field selection includes parent_key automatically | |
| DESCENDANTS-07 | Default ordering by JIRA default (typically issue key) | |
| DESCENDANTS-08 | Custom ordering by specified field | |
| DESCENDANTS-09 | Return page 0 with up to 100 descendants | |
| DESCENDANTS-10 | Return page 1 with next 5 descendants | |
| DESCENDANTS-11 | total_count matches JIRA's childIssuesOf() result count | |
| DESCENDANTS-13 | Fail with "Issue not found" error for non-existent issue | |
| DESCENDANTS-14 | Fail with feature unavailable error when JIRA doesn't support childIssuesOf() | |

## GET_PARENT - Immediate Parent Discovery

| Test ID | Description | Validated |
|---------|-------------|-----------|
| PARENT-01 | Single API call using parentIssuesOf() JQL function | |
| PARENT-02 | Return immediate parent IssueDetails or null | |
| PARENT-03 | Field selection returns only specified fields | |
| PARENT-04 | Return null for root-level issues with no parents | |
| PARENT-05 | Return only immediate parent, not grandparents | |
| PARENT-06 | Parent's own parent_key field correctly populated | |
| PARENT-08 | Default field selection includes all standard fields | |
| PARENT-09 | Fail with "Issue not found" error for non-existent issue | |
| PARENT-10 | Fail with permission error when parent is inaccessible | |
| PARENT-11 | Fail with timeout error for network timeout | |

## GET_ANCESTORS - Ancestor Chain Discovery

| Test ID | Description | Validated |
|---------|-------------|-----------|
| ANCESTORS-01 | Single API call using parentIssuesOf() JQL function | |
| ANCESTORS-02 | Return complete flat list of all ancestors | |
| ANCESTORS-03 | Default field selection includes parent_key for reconstruction | |
| ANCESTORS-04 | Explicit field selection includes parent_key automatically | |
| ANCESTORS-05 | Results unordered - client must reconstruct chain | |
| ANCESTORS-06 | All ancestors include Epic Link and Parent Link fields | |
| ANCESTORS-07 | Parent Link takes precedence over Epic Link | |
| ANCESTORS-09 | total_count matches number of ancestors found | |
| ANCESTORS-10 | has_more: false (ancestors are finite, no paging needed) | |
| ANCESTORS-11 | Fail with "Issue not found" error for non-existent issue | |
| ANCESTORS-12 | Fail with feature unavailable error when JIRA doesn't support parentIssuesOf() | |

## COMMON_BEHAVIORS - Shared Tool Behaviors

| Test ID | Description | Validated |
|---------|-------------|-----------|
| COMMON-01 | Field selection default includes standard fields plus parent_key when required | |
| COMMON-02 | Field selection explicit returns only specified fields | |
| COMMON-03 | parent_key is derived field and cannot be explicitly requested | |
| COMMON-04 | Ordering default uses JIRA's default ordering | |
| COMMON-05 | Ordering explicit uses specified field | |
| COMMON-06 | Paging includes total_count, page_size, current_page, has_more | |
| COMMON-07 | Paging returns up to max_results items starting at start_page | |

## RELIABILITY - Error Handling and Retries (NF2)

| Test ID | Description | Validated |
|---------|-------------|-----------|
| RELIABILITY-02 | Exponential backoff retry for transient failures | |
| RELIABILITY-03 | Maximum 3 retry attempts with 1s, 2s, 4s delays | |
| RELIABILITY-04 | Clear error messages identifying specific failure cause | |
| RELIABILITY-05 | Handle JIRA API rate limits gracefully with backoff | |
| RELIABILITY-06 | Degrade performance rather than fail when rate limited | |
| RELIABILITY-07 | Log rate limit warnings for monitoring | |

## DATA_CONSISTENCY - Field Metadata Caching (NF5)

| Test ID | Description | Validated |
|---------|-------------|-----------|
| CACHE-01 | Pre-load custom field metadata at server startup | |
| CACHE-02 | Cache field discovery results for project:issue_type combinations | |
| CACHE-05 | Fall back to runtime discovery for uncached combinations | |
| CACHE-08 | Graceful fallback when cache miss occurs | |

## DATA_MODELS - Response Structure Validation

| Test ID | Description | Validated |
|---------|-------------|-----------|
| MODELS-01 | IssueDetails model contains all required fields | |
| MODELS-02 | IssueDetails model handles optional fields correctly | |
| MODELS-03 | IssueDetails model includes raw field with complete JIRA response | |
| MODELS-04 | FieldMetadata model contains all required fields | |
| MODELS-05 | FieldMetadata model marks link fields for parent_key derivation | |
| MODELS-06 | PagedResult model includes correct pagination metadata | |
| MODELS-07 | PagedResult model handles empty results correctly | |

## Usage Notes

1. Each test ID maps directly to a test method in the corresponding test file
2. Tests are organized by MCP tool functionality to match requirements structure
3. Success criteria and error conditions from requirements are captured as specific test cases
4. All tests should mock external dependencies (JIRA API calls) for isolation
5. Integration tests may use real JIRA connections but should be clearly separated
6. Performance tests should verify single API call principle and response time limits
7. When adding new functionality, add corresponding test entries to the appropriate tool section
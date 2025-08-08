# MCP JIRA Server Requirements v2

## Table of Contents

- [Overview](#overview)
- [System Boundaries](#system-boundaries)
- [Configuration Requirements](#configuration-requirements)
  - [CF1: Server Configuration](#cf1-server-configuration)
- [Data Models](#data-models)
  - [Core Types](#core-types)
- [Functional Requirements](#functional-requirements)
  - [Common Behaviors](#common-behaviors)
  - [F1: Issue Search and Discovery](#f1-issue-search-and-discovery)
    - [search_issues](#search_issues)
    - [get_issue](#get_issue)
    - [get_field_metadata](#get_field_metadata)
  - [F2: Issue Relationship Discovery](#f2-issue-relationship-discovery)
    - [get_children](#get_children)
    - [get_descendants](#get_descendants)
    - [get_parent](#get_parent)
    - [get_ancestors](#get_ancestors)
- [Non-Functional Requirements](#non-functional-requirements)
  - [NF1: Performance](#nf1-performance)
  - [NF2: Reliability](#nf2-reliability)
  - [NF3: Security](#nf3-security)
  - [NF4: Usability](#nf4-usability)
- [Acceptance Criteria](#acceptance-criteria)

## Overview

This MCP server provides tools for searching and discovering JIRA issues and their relationships. It exposes 7 core tools through the Model Context Protocol for AI assistants to interact with JIRA instances.

MCP Server description considerations:
- **JIRA Issue Key Format:** All tools expect JIRA issue keys in PROJECT-NUMBER format (e.g., "PROJ-123", "EPIC-456", "TASK-789"). This is the standard JIRA identifier format where PROJECT is the project key and NUMBER is the sequential issue number.

## System Boundaries

**In Scope:**
- Read-only access to JIRA issues, projects, and metadata
- Issue relationship discovery (parent-child, links)
- JQL and text-based search capabilities
- Authentication via bearer tokens

**Out of Scope:**
- Creating, updating, or deleting JIRA issues
- Workflow transitions or status changes
- File attachments or comment management
- Administrative functions (user management, project configuration)

## Configuration Requirements

### CF1: Server Configuration

**Purpose:** Configure JIRA connection, authentication, and server behavior.

**Configuration File Format:** YAML file with the following structure:
```yaml
jira:
  base_url: "https://issues.redhat.com"
  authentication:
    type: "bearer_token"
    token: "${JIRA_TOKEN}"  # environment variable reference
  
  # Pre-cache field metadata for these project/issue type combinations
  field_metadata_cache:
    projects:
      - project_key: "RFE"
        sample_issue: "RFE-7877"  # Used to discover available fields via editmeta
      - project_key: "ANSTRAT" 
        sample_issue: "ANSTRAT-1454"
    
  # Optional performance tuning
  api:
    timeout_seconds: 30
    max_retries: 3
    retry_delay_seconds: 1
```

**Configuration Behaviors:**
- **Environment Variables:** Support `${VAR_NAME}` syntax for sensitive values
- **Authentication Types:** Support bearer token authentication
- **Field Discovery:** Use `editmeta` API on sample issues to discover custom parent fields at startup
- **Cache Initialization:** Pre-load field metadata for specified projects to avoid runtime discovery
- **Security:** Never log or expose authentication credentials

**Success Criteria:**
- Configuration file validates on startup with clear error messages for missing/invalid values
- Bearer token authentication works correctly
- Field metadata successfully cached for all configured projects
- Environment variable substitution works for sensitive values
- Invalid sample issues cause startup warnings but don't prevent server start

**Error Conditions:**
- Missing required configuration values → fail startup with specific error
- Invalid JIRA base URL → fail startup with connectivity error
- Authentication failure → fail startup with auth error
- Malformed YAML → fail startup with parsing error

## Data Models

### Core Types

```typescript
interface IssueDetails {
  key: string;                 // "PROJ-123"
  url: string;                 // "https://jira.example.com/browse/PROJ-123"
  summary: string;             // "Fix authentication bug"
  type: string;                // "Story", "Bug", "Epic", "Task"
  status: string;              // "In Progress", "Done", "To Do"
  resolution?: string;         // "Fixed", "Won't Fix", "Duplicate" (if resolved)
  priority?: string;           // "High", "Medium", "Low" (if set)
  assignee?: string;           // "john.doe@company.com" (current assignee)
  reporter?: string;           // "jane.smith@company.com" (who created it)
  created?: string;            // "2024-01-15T10:30:00Z" (ISO timestamp)
  updated?: string;            // "2024-01-20T14:45:00Z" (ISO timestamp)
  description?: string;        // Full issue description (markdown/text)
  acceptance_criteria?: string;// "User can login with SSO" (AC when available)
  parent_key?: string;         // "PROJ-100" (immediate parent issue)
  child_keys?: string[];       // ["PROJ-124", "PROJ-125"] (direct children)
  child_count?: number;        // 5 (number of direct children)
  link_keys?: string[];        // ["PROJ-200", "PROJ-300"] (linked issues)
  link_count?: number;         // 2 (number of issue links)
  raw?: object;                // Complete JIRA API response (optional)
}

interface FieldMetadata {
  id: string;                  // "customfield_12313140"
  name: string;                // "Epic Link"
  description?: string;        // "Links this issue to its epic"
  type: string;               // "epic", "user", "string", "datetime"
  required: boolean;          // true/false
  custom: boolean;            // true for custom fields
  used_for_parent_key: boolean; // true if field name matches .*Link pattern
}

interface PagedResult<T> {
  items: T[];                  // Current page items
  total_count: number;         // Total items available
  page_size: number;           // Items per page (requested)
  current_page: number;        // Current page number (0-based)
  has_more: boolean;           // True if more pages available
}
```

## Functional Requirements

### Common Behaviors

**Field Selection (applies to all tools with `fields` parameter):**
- **Default** (no `fields` parameter): Include all standard fields plus `parent_key` field when required for tool functionality
- **Explicit** (`fields` parameter provided): Return only specified fields
- **Note**: `parent_key` is a derived field and cannot be explicitly requested via `fields` parameter

**Ordering (applies to paged results with `order_by_field` parameter):**
- **Default** (no `order_by_field` parameter): JIRA's default ordering (typically by issue key)
- **Explicit** (`order_by_field` parameter provided): Order results by specified field (e.g., "created", "updated", "status", "priority")

**Paging (applies to all `PagedResult<T>` returns):**
- Return up to `max_results` items starting at page `start_page`
- Include pagination metadata: `total_count`, `page_size`, `current_page`, `has_more`

**Common Error Conditions:**
- Issue key doesn't exist → fail with "Issue not found" error
- JIRA instance doesn't support required JQL functions → fail with feature unavailable error

### F1: Issue Search and Discovery

#### search_issues(query: string, max_results: number = 25, start_page: number = 0, fields: string = null) -> PagedResult<IssueDetails>

**Purpose:** Find JIRA issues using JQL queries or simple text search.

**Behavior:**
- If `query` contains `=`, `AND`, `OR`, or `order by` → treat as JQL
- Otherwise → search issue summaries containing the text
- Return paged result with up to `max_results` issues starting at page `start_page`
- Include pagination metadata (total count, has_more, etc.)
- Sort by JIRA's default relevance scoring
- **Field Selection**: Follow Common Behaviors pattern for `fields` parameter

**Success Criteria:**
- `search_issues("project = PROJ", 25, 0)` returns page 0 (first 25 issues)
- `search_issues("project = PROJ", 25, 1)` returns page 1 (next 25 issues)
- `search_issues("project = PROJ", 25, 0, "key,summary,status")` returns only specified fields
- `has_more: true` when more pages available beyond current page
- `current_page` matches the requested `start_page`
- `total_count` accurately reflects total matching issues
- No issues found returns empty items array with `total_count: 0` and `has_more: false`

**Error Conditions:**
- Invalid JQL syntax → fail with specific syntax error
- Authentication failure → fail with authentication error
- Network timeout → fail with timeout error

#### get_issue(key: string, fields?: string) -> IssueDetails

**Purpose:** Retrieve complete information for a specific JIRA issue.

**Behavior:**
- Return issue details including description, status, assignee, and relationship fields
- Support field selection (e.g., "key,summary,status,customfield_12313140,customfield_12311140")
- Include parent relationship fields: Epic Link and Parent Link in raw field
- Consolidate parent relationship fields into a single "parent_key" response field.
- Raw field contains complete JIRA API response for additional custom field access

**Success Criteria:**
- `get_issue("PROJ-123")` returns complete issue data with all standard fields
- `get_issue("PROJ-123", "key,summary,status,assignee")` returns only specified fields
- Raw field contains all JIRA API data including custom relationship fields

**Error Conditions:**
- Issue key doesn't exist → fail with "Issue not found" error
- Issue exists but user lacks permission → fail with permission error
- Invalid issue key format → fail with format validation error

#### get_field_metadata(project_key: string, sample_issue?: string, issue_type?: string) -> FieldMetadata[]

**Purpose:** Retrieve available field metadata for a project and identify parent relationship fields.

**Behavior:**
- **Parameter Usage (choose one approach):**
  - **Preferred:** Provide `sample_issue` - uses `editmeta` API to discover available fields, determines issue type automatically, caches results
  - **Alternative:** Provide `issue_type` - cache-only lookup, no API calls, fails fast on cache miss
  - **Invalid:** Cannot provide both `sample_issue` and `issue_type` parameters
- Return field metadata including which fields are used for `parent_key` derivation
- Mark fields with names matching `.*Link` pattern as `used_for_parent_key: true`
- Cache discovered metadata for future use using simple in-memory storage

**LLM Usage Guidance:**
- **When you know an issue key:** Use `get_field_metadata("PROJ", "PROJ-123")` - this will discover and cache field metadata
- **When you know project + issue type and want fast cache-only lookup:** Use `get_field_metadata("PROJ", null, "Story")` - fails if not cached
- **Invalid query:** `get_field_metadata("PROJ")` will fail, must supply one of `sample_issue` or `issue_type`

**Success Criteria:**
- `get_field_metadata("RFE", "RFE-1")` discovers and caches metadata using sample issue
- `get_field_metadata("RFE", null, "Feature Request")` returns cached metadata for RFE Feature Request (cache-only)
- `get_field_metadata("RFE", "RFE-1", "Feature Request")` fails
- `get_field_metadata("RFE")` fails
- Fields like "Epic Link", "Parent Link", "Feature Link" have `used_for_parent_key: true`
- Non-link fields have `used_for_parent_key: false`
- Metadata includes field type, description, and requirement status

**Error Conditions:**
- Both `sample_issue` and `issue_type` provided → fail with parameter validation error
- Project key doesn't exist (with sample_issue) → fail with "Project not found" error
- Sample issue doesn't exist → fail with "Sample issue not found" error
- Insufficient permissions for editmeta → fail with permission error
- No cached data exists (with issue_type or no parameters) → fail with cache miss error

#### get_known_parent_fields() -> string[]

**Purpose:** Get list of all known parent fields across all cached projects and issue types for dynamic parent field resolution.

**Behavior:**
- Cache-only lookup - no JIRA API calls performed
- Return all unique fields where `used_for_parent_key: true` from entire cache
- Convenience function for ancestor/hierarchy queries where issue types are unknown
- Optimized for use in `get_ancestors` and other hierarchy traversal operations
- When querying single issue type (like `get_children`), use `get_field_metadata` with `issue_type` parameter instead

**Success Criteria:**
- `get_known_parent_fields()` returns `["customfield_12313140", "customfield_12311140", "customfield_12345678"]` 
- Returns deduplicated fields across all cached project::issue_type combinations
- Only returns fields, not full metadata objects
- No JIRA API calls are made

**Error Conditions:**
- No cached field metadata exists anywhere → returns empty array (graceful degradation)

### F2: Issue Relationship Discovery

#### get_children(issue_key: string, max_results: number = 100, start_page: number = 0, fields?: string, order_by_field?: string) -> PagedResult<IssueDetails>

**Purpose:** Find immediate child issues (1 level down).

**Behavior:**
- Use efficient JQL queries for parent-link discovery  
- Follows common field selection, ordering, and paging behaviors (see Common Behaviors)

**Success Criteria:**
- `get_children("EPIC-123")` returns page 0 (first 100 direct child issues) with all standard fields + parent relationship fields
- `get_children("EPIC-123", 50, 0)` page 0 with 50 results  
- `get_children("EPIC-123", 50, 1)` page 1 with 50 results
- `get_children("EPIC-123", 100, 0, "key,summary,status")` returns only specified fields
- `get_children("EPIC-123", 100, 0, null, "created")` returns results ordered by creation date
- `get_children("EPIC-123", 100, 0, "key,summary,status", "priority")` returns specified fields ordered by priority
- Empty result with `total_count: 0` for issues with no children

**Error Conditions:**
- Issue key doesn't exist → fail with "Issue not found" error
- Rate limit exceeded → fail with rate limit error after retries

#### get_descendants(issue_key: string, max_results: number = 100, start_page: number = 0, fields?: string, order_by_field?: string) -> PagedResult<IssueDetails>

**Purpose:** Find all descendant issues in hierarchy (flat list with relationship metadata for tree reconstruction).

**Behavior:**
- Single JIRA API call using `childIssuesOf("ISSUE-123")` JQL function
- Return paged flat list of all descendants with relationship fields populated
- **Result Requirements:**
  - Search root issue is NOT included in results (only descendants)
  - Every descendant MUST have `parent_key` field populated
  - All descendants form a connected hierarchy tree rooted at the search issue
- **Field Selection Behavior:**
  - **Default** (no `fields` parameter): Include all standard fields plus `parent_key` field (required for hierarchy reconstruction)
  - **Explicit** (`fields` parameter provided): Return only specified fields plus `parent_key` field (always included for tool functionality)
- **Ordering Behavior:**
  - **Default** (no `order_by_field` parameter): JIRA's default ordering (typically by issue key)
  - **Explicit** (`order_by_field` parameter provided): Order results by specified field (e.g., "created", "updated", "status", "priority")
- Client must reconstruct hierarchy using parent relationship fields

**Hierarchy Reconstruction Guide:**
To build a tree structure from the flat result:
1. **All descendants have parent_key** - Every issue in the response MUST have a `parent_key` field populated (no descendants without parents)
2. **Search root not included** - The search issue itself is NOT included in the descendants results
3. **Identify immediate children** of the search root by finding issues where:
   - `parent_key` == search root key
4. **For each descendant**, determine its immediate parent by checking its `parent_key` value
5. **Build tree recursively** by grouping descendants under their immediate parents


**Example Tree Reconstruction:**
```
Search: get_descendants("EPIC-123")
Flat Results: [FEATURE-456, TASK-789, TASK-790]

Analysis:
- FEATURE-456: parent_key="EPIC-123" → direct child of EPIC-123
- TASK-789: parent_key="FEATURE-456" → child of FEATURE-456  
- TASK-790: parent_key="FEATURE-456" → child of FEATURE-456

Reconstructed Tree:
EPIC-123 (search root)
└── FEATURE-456
    ├── TASK-789
    └── TASK-790
```

**Implementation Example:**
```bash
# JQL Query
GET /search?jql=issuekey in childIssuesOf("EPIC-123")&fields=key,summary,status,customfield_12313140,customfield_12311140&startAt=0&maxResults=100

# Expected Result Structure
{
  "total": 590,
  "issues": [
    {
      "key": "FEATURE-456",
      "fields": {
        "summary": "User Authentication",
        "status": {"name": "In Progress"},
        "customfield_12313140": "EPIC-123",     // Epic Link points to root
        "customfield_12311140": null            // No parent link
      }
    },
    {
      "key": "TASK-789", 
      "fields": {
        "summary": "Login API",
        "status": {"name": "Done"},
        "customfield_12313140": null,           // No epic link
        "customfield_12311140": "FEATURE-456"  // Parent link points to feature
      }
    }
  ]
}
```

**Success Criteria:**
- `get_descendants("EPIC-123", 100, 0)` returns page 0 with up to 100 descendants
- `get_descendants("EPIC-123", 100, 1)` returns page 1 with next 100 descendants  
- All descendants "parent_key" attribute for tree reconstruction
- `total_count` matches JIRA's `childIssuesOf()` result count
- Performance: single API call regardless of hierarchy size

**Error Conditions:**
- Issue key doesn't exist → fail with "Issue not found" error
- JIRA instance doesn't support `childIssuesOf()` function → fail with feature unavailable error

#### get_parent(issue_key: string, fields?: string) -> IssueDetails | null

**Purpose:** Find immediate parent issue (1 level up).

**Behavior:**
- Single JIRA API call using `parentIssuesOf("CHILD-123")` JQL function  
- Return only the immediate parent (first/closest ancestor)
- Support field selection (e.g., "key,summary,status") like `get_issue`
- Return null if the JQL returns no results (root-level issue)
- **Field Selection Behavior:**
  - **Default** (no `fields` parameter): Include all standard fields
  - **Explicit** (`fields` parameter provided): Return only specified fields

**Success Criteria:**
- `get_parent("STORY-456")` returns immediate parent IssueDetails (or null if no parent)
- `get_parent("STORY-456", "key,summary,status")` returns parent with only specified fields
- Returns null for root-level issues with no parents
- Returns only the immediate parent, not grandparents or higher ancestors
- Parent's own `parent_key` field correctly populated in response
- Performance: single API call regardless of hierarchy depth

**Error Conditions:**
- Issue key doesn't exist → fail with "Issue not found" error  
- Parent exists but is inaccessible → fail with permission error
- Network timeout → fail with timeout error

#### get_ancestors(issue_key: string, fields?: string) -> PagedResult<IssueDetails>

**Purpose:** Find all ancestor issues up the hierarchy (flat list with relationship metadata for chain reconstruction).

**Behavior:**
- Single JIRA API call using `parentIssuesOf("ISSUE-123")` JQL function
- Return complete flat list of all ancestors with relationship fields populated
- **Field Selection Behavior:**
  - **Default** (no `fields` parameter): Include all standard fields plus `parent_key` field for chain reconstruction
  - **Explicit** (`fields` parameter provided): Return only specified fields - `parent_key` field is always included automatically
- Results are unordered - client must reconstruct ancestor chain using parent relationship fields

**Chain Reconstruction Guide:**
To build an ordered ancestor chain from the flat result:
1. **Find the immediate parent** of the search issue by checking each ancestor's `parent_key` field
2. **Build chain recursively** by following parent relationships:
   - Start with immediate parent (ancestor whose child is the search issue)
   - Find its parent by checking its `parent_key` field
   - Continue until reaching an ancestor with no `parent_key` (root)
3. **Order the chain** from immediate parent to root

**Example Chain Reconstruction:**
```
Search: get_ancestors("TASK-789")
Flat Results: [FEATURE-456, EPIC-123, INITIATIVE-1]

Analysis:
- FEATURE-456: parent_key="EPIC-123" → parent is EPIC-123
- EPIC-123: parent_key="INITIATIVE-1" → parent is INITIATIVE-1  
- INITIATIVE-1: parent_key=null → root (no parent)

Reconstructed Chain (ordered):
TASK-789 (search issue)
← FEATURE-456 (immediate parent)  
← EPIC-123 (grandparent)
← INITIATIVE-1 (root)
```

**Implementation Example:**
```bash
# JQL Query  
GET /search?jql=issuekey in parentIssuesOf("TASK-789")&fields=key,summary,status,customfield_12313140,customfield_12311140

# Expected Result Structure
{
  "total": 3,
  "issues": [
    {
      "key": "FEATURE-456",
      "fields": {
        "summary": "User Authentication",
        "customfield_12313140": "EPIC-123",     // This feature belongs to epic
        "customfield_12311140": null
      }
    },
    {
      "key": "EPIC-123",
      "fields": {
        "summary": "Authentication System", 
        "customfield_12313140": null,
        "customfield_12311140": "INITIATIVE-1" // Epic belongs to initiative
      }
    },
    {
      "key": "INITIATIVE-1",
      "fields": {
        "summary": "Platform Security",
        "customfield_12313140": null,
        "customfield_12311140": null            // Root level
      }
    }
  ]
}
```

**Success Criteria:**
- `get_ancestors("TASK-789")` returns all ancestors in `items` array (unordered)
- All ancestors include Epic Link and Parent Link custom fields populated
- Client can reconstruct ordered ancestor chain using the relationship reconstruction guide
- Parent Link (`customfield_12311140`) takes precedence over Epic Link (`customfield_12313140`)
- Performance: single API call regardless of hierarchy depth
- `total_count` matches number of ancestors found  
- `has_more: false` (ancestors are finite, no paging needed)

**Error Conditions:**
- Issue key doesn't exist → fail with "Issue not found" error
- JIRA instance doesn't support `parentIssuesOf()` function → fail with feature unavailable error

## Non-Functional Requirements

### NF1: Performance

**Single API Call Principle:**
- All MCP tools must complete with exactly one JIRA API call
- Response time bounded by single API call latency (typically 1-5 seconds)
- No recursive calls, no client-side aggregation of multiple API responses

**Throughput:**
- Predictable resource usage per tool call
- Support concurrent usage without rate limit accumulation


### NF2: Reliability

**Error Handling:**
- All tools must fail clearly or succeed completely (no partial results)
- Exponential backoff retry for transient failures (rate limits, network)
- Maximum 3 retry attempts with 1s, 2s, 4s delays
- Clear error messages identifying specific failure cause

**Rate Limiting:**
- Handle JIRA API rate limits gracefully with backoff
- Degrade performance rather than fail when rate limited
- Log rate limit warnings for monitoring

### NF3: Security

**Authentication:**
- Support bearer token authentication
- Never log authentication credentials

**Authorization:**
- Respect JIRA permission model
- Fail clearly when user lacks permission for specific issues

### NF4: Usability

**Error Messages:**
- Identify specific failure cause (network, auth, not found, rate limit)
- Include remediation suggestions where appropriate
- Distinguish between configuration errors and transient failures

**Tool Descriptions:**
- Provide clear purpose and use case for each tool
- Include parameter explanations and examples
- Specify when to use each tool vs alternatives
- Document performance characteristics and limitations

### NF5: Data Consistency

**Field Metadata Caching:**
- Pre-load custom field metadata at server startup
- Cache field discovery results for project:issue_type combinations
- Never invalidate cache during runtime (restart required for refresh)
- Fall back to runtime discovery for uncached combinations

**Cache Behavior:**
- Cache persists for entire server session
- No automatic expiration or invalidation
- Restart server to refresh cached field metadata
- Graceful fallback when cache miss occurs

## Quality Attributes

### Maintainability
- Modular tool design with clear separation of concerns
- Standardized error handling patterns across all tools
- Minimal code duplication between relationship discovery tools

### Testability
- Each tool has deterministic behavior for given inputs
- Clear success/failure criteria for automated testing
- Isolated dependencies for unit testing

### Observability
- Log API calls and response times for performance monitoring

## Acceptance Criteria

**Deployment:**
- Server starts successfully with valid JIRA configuration
- All tools register correctly with MCP protocol
- Authentication works for configured JIRA instance

**Basic Operations:**
- Search finds relevant issues for test queries
- Issue retrieval returns complete data for valid keys
- Relationship discovery works for test issue hierarchies

**Error Handling:**
- Invalid inputs produce clear error messages
- Network failures retry appropriately before failing
- Rate limit handling prevents tool failures

**Performance:**
- Response times meet specified limits for test data sets
- Large hierarchies complete successfully within timeout limits
- Cache pre-loading improves relationship discovery performance
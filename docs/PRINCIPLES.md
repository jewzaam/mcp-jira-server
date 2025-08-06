# MCP JIRA Server Design Principles

## Single Responsibility Principle

Each MCP tool should have a single, well-defined responsibility and should accomplish that responsibility with minimal API complexity.

### Metric: One Tool Call = One API Call

**Principle:** A correctly designed MCP tool should require only a single JIRA API call to fulfill its purpose.

**Rationale:**
- **Predictable performance** - Execution time is bounded by single API call latency
- **Reliable resource usage** - Memory and network usage is predictable  
- **Simple error handling** - Only one point of failure per tool call
- **Rate limit friendly** - Minimal API consumption per operation
- **Testable** - Easy to mock and unit test with single API interaction

## Benefits

Following this principle ensures:
- **Predictable performance** - No surprise timeouts or memory issues
- **Reliable behavior** - Consistent response times and resource usage
- **Simple debugging** - Clear API call -> response mapping
- **Scalable architecture** - Each tool scales independently
- **Composable operations** - Complex workflows built from simple primitives
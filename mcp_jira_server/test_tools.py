#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Tools

This test module provides comprehensive coverage for the MCP tools
functionality including search_issues, get_issue, and identifier_hint.
"""

import unittest
from unittest.mock import Mock
import asyncio

# Import modules under test  
from mcp_jira_server.server import JiraTools, IssueSummary, IssueDetails


class TestTools(unittest.TestCase):
    """Test MCP tool implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client.base_url = "https://test.jira.com"
        self.mock_client.api_base = "https://test.jira.com/rest/api/2"
        self.tools = JiraTools(self.mock_client)

    def test_tools_01_search_issues_with_simple_text_query(self):
        """TOOLS-01: Search issues with simple text query."""
        self.mock_client._make_api_request.return_value = {
            "issues": [{
                "key": "TEST-123",
                "fields": {
                    "summary": "Test issue",
                    "status": {"name": "Open"}
                }
            }]
        }
        
        result = asyncio.run(self.tools.search_issues("simple search"))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].key, "TEST-123")
        self.assertEqual(result[0].summary, "Test issue")
        self.assertEqual(result[0].status, "Open")

    def test_tools_02_search_issues_with_jql_query(self):
        """TOOLS-02: Search issues with JQL query."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        asyncio.run(self.tools.search_issues("project = TEST AND status = Open"))
        
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertIn("jql", kwargs["params"])
        self.assertEqual(kwargs["params"]["jql"], "project = TEST AND status = Open")

    def test_tools_03_search_issues_with_jql_detection_equals_sign(self):
        """TOOLS-03: Search issues with JQL detection (equals sign)."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        asyncio.run(self.tools.search_issues("project = TEST"))
        
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["jql"], "project = TEST")

    def test_tools_04_search_issues_with_jql_detection_and_or_operators(self):
        """TOOLS-04: Search issues with JQL detection (AND/OR operators)."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        asyncio.run(self.tools.search_issues("status = Open AND assignee = currentUser()"))
        
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["jql"], "status = Open AND assignee = currentUser()")

    def test_tools_05_search_issues_with_max_results_parameter(self):
        """TOOLS-05: Search issues with max results parameter."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        asyncio.run(self.tools.search_issues("test", max_results=50))
        
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["maxResults"], 50)

    def test_tools_06_search_issues_with_max_results_boundary(self):
        """TOOLS-06: Search issues with max results boundary (1-100)."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        # Test lower boundary
        asyncio.run(self.tools.search_issues("test", max_results=0))
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["maxResults"], 1)
        
        # Test upper boundary
        asyncio.run(self.tools.search_issues("test", max_results=150))
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["maxResults"], 100)

    def test_tools_07_search_issues_returns_proper_issue_summary_objects(self):
        """TOOLS-07: Search issues returns proper IssueSummary objects."""
        self.mock_client._make_api_request.return_value = {
            "issues": [{
                "key": "TEST-456",
                "fields": {
                    "summary": "Another test issue",
                    "status": {"name": "In Progress"}
                }
            }]
        }
        
        result = asyncio.run(self.tools.search_issues("test"))
        
        self.assertIsInstance(result[0], IssueSummary)
        self.assertEqual(result[0].url, "https://test.jira.com/browse/TEST-456")

    def test_tools_08_get_single_issue_by_key(self):
        """TOOLS-08: Get single issue by key."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-789",
            "fields": {
                "summary": "Single issue test",
                "description": "Test description",
                "status": {"name": "Done"}
            }
        }
        
        result = asyncio.run(self.tools.get_issue("TEST-789"))
        
        self.mock_client.get_issue.assert_called_once_with("TEST-789", expand=None)
        self.assertEqual(result.key, "TEST-789")
        self.assertEqual(result.summary, "Single issue test")
        self.assertEqual(result.description, "Test description")
        self.assertEqual(result.status, "Done")

    def test_tools_09_get_issue_with_expand_parameter(self):
        """TOOLS-09: Get issue with expand parameter."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-999",
            "fields": {
                "summary": "Expanded issue",
                "status": {"name": "Open"}
            }
        }
        
        asyncio.run(self.tools.get_issue("TEST-999", expand="changelog,comments"))
        
        self.mock_client.get_issue.assert_called_once_with("TEST-999", expand="changelog,comments")

    def test_tools_10_get_issue_returns_proper_issue_details_object(self):
        """TOOLS-10: Get issue returns proper IssueDetails object."""
        issue_data = {
            "key": "TEST-111",
            "fields": {
                "summary": "Details test",
                "description": None,
                "status": {"name": "Closed"}
            }
        }
        self.mock_client.get_issue.return_value = issue_data
        
        result = asyncio.run(self.tools.get_issue("TEST-111"))
        
        self.assertIsInstance(result, IssueDetails)
        self.assertEqual(result.description, None)
        self.assertEqual(result.raw, issue_data)

    def test_tools_11_identifier_hint_returns_expected_format_description(self):
        """TOOLS-11: Identifier hint returns expected format description."""
        result = asyncio.run(self.tools.identifier_hint())
        
        self.assertIn("PROJECT>-<NUMBER>", result)
        self.assertIn("RFE-7877", result)


if __name__ == "__main__":
    unittest.main(verbosity=2) 
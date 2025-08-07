#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Integration

This test module provides comprehensive coverage for integration between
different components of the MCP JIRA server.

Test IDs: INTEGRATION-01 through INTEGRATION-03
"""

import unittest
from unittest.mock import Mock, patch
import asyncio

# Import modules under test
from mcp_jira_server.server import JiraTools


class TestIntegration(unittest.TestCase):
    """Test component integration."""

    def test_integration_01_jira_tools_initialization_with_client(self):
        """INTEGRATION-01: JiraTools initialization with client."""
        mock_client = Mock()
        tools = JiraTools(mock_client)
        
        self.assertEqual(tools._client, mock_client)
        self.assertIsNotNone(tools._logger)

    @patch("mcp_jira_server.server.JiraClient")
    def test_integration_02_search_tool_integration_with_jira_client(self, mock_client_class):
        """INTEGRATION-02: Search tool integration with JiraClient."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client._make_api_request.return_value = {"issues": []}
        mock_client_class.return_value = mock_client
        
        tools = JiraTools(mock_client)
        asyncio.run(tools.search_issues("test query"))
        
        mock_client._make_api_request.assert_called_once()

    def test_integration_03_get_issue_tool_integration_with_jira_client(self):
        """INTEGRATION-03: Get issue tool integration with JiraClient."""
        mock_client = Mock()
        mock_client.get_issue.return_value = {
            "key": "INT-123",
            "fields": {
                "summary": "Integration test",
                "status": {"name": "Open"}
            }
        }
        
        tools = JiraTools(mock_client)
        result = asyncio.run(tools.get_issue("INT-123"))
        
        mock_client.get_issue.assert_called_once_with("INT-123", expand=None)
        self.assertEqual(result.key, "INT-123")

    def test_integration_04_tool_error_handling_for_authentication_failures(self):
        """INTEGRATION-04: Tool error handling for authentication failures."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client._make_api_request.side_effect = Exception("401 Unauthorized")
        
        tools = JiraTools(mock_client)
        
        with self.assertRaises(Exception) as cm:
            asyncio.run(tools.search_issues("test"))
        
        self.assertIn("401", str(cm.exception))

    def test_integration_05_tool_error_handling_for_network_errors(self):
        """INTEGRATION-05: Tool error handling for network errors."""
        mock_client = Mock()
        mock_client.get_issue.side_effect = ConnectionError("Network unreachable")
        
        tools = JiraTools(mock_client)
        
        with self.assertRaises(ConnectionError) as cm:
            asyncio.run(tools.get_issue("NET-123"))
        
        self.assertIn("Network", str(cm.exception))

    def test_integration_06_tool_error_handling_for_api_errors(self):
        """INTEGRATION-06: Tool error handling for API errors."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client._make_api_request.side_effect = Exception("500 Internal Server Error")
        
        tools = JiraTools(mock_client)
        
        with self.assertRaises(Exception) as cm:
            asyncio.run(tools.search_issues("test"))
        
        self.assertIn("500", str(cm.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2) 
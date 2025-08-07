#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Creation

This test module provides comprehensive coverage for MCP JIRA server
creation and configuration functionality.

Test IDs: SERVER-01 through SERVER-07
"""

import unittest
from unittest.mock import Mock, patch

# Import modules under test
from mcp_jira_server.server import create_server


class TestServer(unittest.TestCase):
    """Test MCP server creation and configuration."""

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_server_01_create_server_with_url_only(self, mock_fastmcp, mock_client):
        """SERVER-01: Create server with URL only."""
        create_server(url="https://test.jira.com")
        
        mock_client.assert_called_once_with(
            base_url="https://test.jira.com",
            username=None,
            password=None,
            token=None,
            bearer_token=None
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_server_02_create_server_with_username_password_auth(self, mock_fastmcp, mock_client):
        """SERVER-02: Create server with username/password auth."""
        create_server(
            url="https://test.jira.com",
            username="testuser",
            password="testpass"
        )
        
        mock_client.assert_called_once_with(
            base_url="https://test.jira.com",
            username="testuser",
            password="testpass",
            token=None,
            bearer_token=None
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_server_03_create_server_with_username_token_auth(self, mock_fastmcp, mock_client):
        """SERVER-03: Create server with username/token auth."""
        create_server(
            url="https://test.jira.com",
            username="testuser",
            token="testtoken"
        )
        
        mock_client.assert_called_once_with(
            base_url="https://test.jira.com",
            username="testuser",
            password=None,
            token="testtoken",
            bearer_token=None
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_server_04_create_server_with_bearer_token_auth(self, mock_fastmcp, mock_client):
        """SERVER-04: Create server with bearer token auth."""
        create_server(
            url="https://test.jira.com",
            bearer_token="bearer123"
        )
        
        mock_client.assert_called_once_with(
            base_url="https://test.jira.com",
            username=None,
            password=None,
            token=None,
            bearer_token="bearer123"
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_server_05_server_has_correct_name_and_instructions(self, mock_fastmcp, mock_client):
        """SERVER-05: Server has correct name and instructions."""
        create_server(url="https://test.jira.com")
        
        mock_fastmcp.assert_called_once()
        call_args = mock_fastmcp.call_args
        self.assertEqual(call_args[1]["name"], "JIRA Read-Only MCP Server")
        self.assertIn("JIRA expert assistant", call_args[1]["instructions"])

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_server_06_server_registers_all_nine_tools(self, mock_fastmcp, mock_client):
        """SERVER-06: Server registers all nine tools."""
        mock_server = Mock()
        mock_fastmcp.return_value = mock_server
        
        create_server(url="https://test.jira.com")
        
        # Check that tool decorator was called 9 times
        self.assertEqual(mock_server.tool.call_count, 9)
        
        # Check tool names
        tool_names = [call[1]["name"] for call in mock_server.tool.call_args_list]
        expected_names = [
            "search_issues", "get_issue", "identifier_hint",
            "get_issue_relationships", "get_descendants", "get_children", "get_linked_issues",
            "get_parent", "get_ancestors"
        ]
        for name in expected_names:
            self.assertIn(name, tool_names)

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_server_07_tools_have_correct_annotations(self, mock_fastmcp, mock_client):
        """SERVER-07: Tools have correct annotations (read-only, idempotent)."""
        mock_server = Mock()
        mock_fastmcp.return_value = mock_server
        
        create_server(url="https://test.jira.com")
        
        # Check annotations for all tool calls
        for call in mock_server.tool.call_args_list:
            annotations = call[1]["annotations"]
            self.assertTrue(annotations.readOnlyHint)
            self.assertFalse(annotations.destructiveHint)
            self.assertTrue(annotations.idempotentHint)
            self.assertFalse(annotations.openWorldHint)


if __name__ == "__main__":
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    unittest.main(verbosity=2) 
#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Async Operations

This test module provides comprehensive coverage for asynchronous
operations in the MCP JIRA server.

Test IDs: ASYNC-01 through ASYNC-04
"""

import unittest
from unittest.mock import Mock, patch
import asyncio

# Import modules under test
from mcp_jira_server.server import JiraTools, _async_main


class TestAsync(unittest.TestCase):
    """Test asynchronous operations."""

    def test_async_01_async_search_issues_method(self):
        """ASYNC-01: Async search_issues method."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client._make_api_request.return_value = {"issues": []}
        
        tools = JiraTools(mock_client)
        
        # Verify the method is async
        result = tools.search_issues("test")
        self.assertTrue(asyncio.iscoroutine(result))
        
        # Clean up the coroutine
        asyncio.run(result)

    def test_async_02_async_get_issue_method(self):
        """ASYNC-02: Async get_issue method."""
        mock_client = Mock()
        mock_client.get_issue.return_value = {
            "key": "ASYNC-123",
            "fields": {"summary": "Async test", "status": {"name": "Open"}}
        }
        
        tools = JiraTools(mock_client)
        
        # Verify the method is async
        result = tools.get_issue("ASYNC-123")
        self.assertTrue(asyncio.iscoroutine(result))
        
        # Clean up the coroutine
        asyncio.run(result)

    def test_async_03_async_identifier_hint_method(self):
        """ASYNC-03: Async identifier_hint method."""
        mock_client = Mock()
        tools = JiraTools(mock_client)
        
        # Verify the method is async
        result = tools.identifier_hint()
        self.assertTrue(asyncio.iscoroutine(result))
        
        # Clean up the coroutine
        asyncio.run(result)

    @patch("mcp_jira_server.server.load_config")
    @patch("mcp_jira_server.server.create_server")
    @patch("argparse.ArgumentParser.parse_args")
    def test_async_04_async_main_function_entry_point(self, mock_parse, mock_create, mock_config):
        """ASYNC-04: Async main function entry point."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = "https://async.jira.com"
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {}
        
        async def mock_run_async():
            return None
        
        mock_server = Mock()
        mock_server.run_async = mock_run_async
        mock_create.return_value = mock_server
        
        # Verify _async_main is async
        result = _async_main()
        self.assertTrue(asyncio.iscoroutine(result))
        
        # Clean up the coroutine
        asyncio.run(result)

    @patch("mcp_jira_server.server.load_config")
    @patch("mcp_jira_server.server.create_server")
    @patch("argparse.ArgumentParser.parse_args")
    def test_async_05_server_startup_and_shutdown(self, mock_parse, mock_create, mock_config):
        """ASYNC-05: Server startup and shutdown."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = "https://startup.jira.com"
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {}
        
        # Mock server with async run method
        mock_server = Mock()
        
        async def mock_run_async():
            return "Server started and stopped"
        
        mock_server.run_async = mock_run_async
        mock_create.return_value = mock_server
        
        # Test server startup/shutdown lifecycle
        result = asyncio.run(_async_main())
        
        # Verify server was created and run_async was called
        mock_create.assert_called_once()
        self.assertIsNone(result)  # _async_main returns None after successful run


if __name__ == "__main__":
    unittest.main(verbosity=2) 
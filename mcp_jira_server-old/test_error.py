#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Error Handling

This test module provides comprehensive coverage for error handling
in the MCP JIRA server.
"""

import unittest
from unittest.mock import Mock, patch
import asyncio
import yaml
from pathlib import Path
from pyfakefs.fake_filesystem_unittest import TestCase

from mcp_jira_server.server import JiraTools
from mcp_jira_server.config import _load_from_file, ConfigError


class TestError(TestCase):
    """Test error handling functionality."""

    def setUp(self):
        """Set up fake filesystem for each test."""
        self.setUpPyfakefs()

    def test_error_01_handle_jira_client_exceptions_in_search(self):
        """ERROR-01: Handle JiraClient exceptions in search."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client._make_api_request.side_effect = Exception("Connection failed")
        
        tools = JiraTools(mock_client)
        
        with self.assertRaises(Exception) as cm:
            asyncio.run(tools.search_issues("test"))
        
        self.assertIn("Connection failed", str(cm.exception))

    def test_error_02_handle_jira_client_exceptions_in_get_issue(self):
        """ERROR-02: Handle JiraClient exceptions in get_issue."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client._make_api_request.side_effect = Exception("Issue not found")
        
        tools = JiraTools(mock_client)
        
        with self.assertRaises(Exception):
            asyncio.run(tools.get_issue("NOTFOUND-123"))

    def test_error_03_handle_malformed_configuration_files(self):
        """ERROR-03: Handle malformed configuration files."""
        invalid_yaml = "invalid: yaml: content: ["
        self.fs.create_file("/test/invalid.yaml", contents=invalid_yaml)
        
        with self.assertRaises(yaml.YAMLError):
            _load_from_file(Path("/test/invalid.yaml"))

    @patch("mcp_jira_server.server.load_config")
    @patch("argparse.ArgumentParser.parse_args")
    def test_error_04_handle_missing_required_configuration(self, mock_parse, mock_config):
        """ERROR-04: Handle missing required configuration."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = None
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {}
        
        from mcp_jira_server.server import main
        
        with self.assertRaises(ConfigError) as cm:
            main()
        
        self.assertIn("url", str(cm.exception))

    def test_error_05_handle_invalid_issue_keys(self):
        """ERROR-05: Handle invalid issue keys."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client.get_issue.side_effect = Exception("Invalid issue key format")
        
        tools = JiraTools(mock_client)
        
        with self.assertRaises(Exception) as cm:
            asyncio.run(tools.get_issue("INVALID"))
        
        self.assertIn("Invalid issue key", str(cm.exception))

    def test_error_06_handle_network_timeouts(self):
        """ERROR-06: Handle network timeouts."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client._make_api_request.side_effect = TimeoutError("Request timed out")
        
        tools = JiraTools(mock_client)
        
        with self.assertRaises(TimeoutError) as cm:
            asyncio.run(tools.search_issues("test"))
        
        self.assertIn("timed out", str(cm.exception))

    def test_error_07_handle_http_error_responses(self):
        """ERROR-07: Handle HTTP error responses."""
        mock_client = Mock()
        mock_client.api_base = "https://test.jira.com/rest/api/2"
        mock_client._make_api_request.side_effect = Exception("404 Not Found")
        
        tools = JiraTools(mock_client)
        
        with self.assertRaises(Exception) as cm:
            asyncio.run(tools.search_issues("test"))
        
        self.assertIn("404", str(cm.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2) 
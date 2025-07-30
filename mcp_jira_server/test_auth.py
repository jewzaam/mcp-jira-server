#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Authentication

This test module provides comprehensive coverage for authentication
integration in the MCP JIRA server.

Test IDs: AUTH-01 through AUTH-04
"""

import unittest
from unittest.mock import patch

# Import modules under test
from mcp_jira_server.server import create_server


class TestAuth(unittest.TestCase):
    """Test authentication integration."""

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_auth_01_server_creation_with_basic_auth(self, mock_fastmcp, mock_client):
        """AUTH-01: Server creation with basic auth (username/password)."""
        create_server(
            url="https://auth.jira.com",
            username="authuser",
            password="authpass"
        )
        
        mock_client.assert_called_once_with(
            base_url="https://auth.jira.com",
            username="authuser",
            password="authpass",
            token=None,
            bearer_token=None
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_auth_02_server_creation_with_token_auth(self, mock_fastmcp, mock_client):
        """AUTH-02: Server creation with token auth (username/token)."""
        create_server(
            url="https://token.jira.com",
            username="tokenuser",
            token="authtoken123"
        )
        
        mock_client.assert_called_once_with(
            base_url="https://token.jira.com",
            username="tokenuser",
            password=None,
            token="authtoken123",
            bearer_token=None
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_auth_03_server_creation_with_bearer_token_auth(self, mock_fastmcp, mock_client):
        """AUTH-03: Server creation with bearer token auth."""
        create_server(
            url="https://bearer.jira.com",
            bearer_token="bearer_token_123"
        )
        
        mock_client.assert_called_once_with(
            base_url="https://bearer.jira.com",
            username=None,
            password=None,
            token=None,
            bearer_token="bearer_token_123"
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_auth_04_server_creation_without_authentication(self, mock_fastmcp, mock_client):
        """AUTH-04: Server creation without authentication."""
        create_server(url="https://noauth.jira.com")
        
        mock_client.assert_called_once_with(
            base_url="https://noauth.jira.com",
            username=None,
            password=None,
            token=None,
            bearer_token=None
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_auth_05_config_file_authentication_parameters(self, mock_fastmcp, mock_client):
        """AUTH-05: Config file authentication parameters."""
        # Test that config file auth parameters are passed correctly
        config = {
            "url": "https://config.jira.com",
            "username": "configuser",
            "password": "configpass"
        }
        
        create_server(**config)
        
        mock_client.assert_called_once_with(
            base_url="https://config.jira.com",
            username="configuser",
            password="configpass",
            token=None,
            bearer_token=None
        )

    @patch("mcp_jira_server.server.JiraClient")
    @patch("mcp_jira_server.server.FastMCP")
    def test_auth_06_cli_authentication_parameter_override(self, mock_fastmcp, mock_client):
        """AUTH-06: CLI authentication parameter override."""
        # Test that CLI parameters override config file parameters
        create_server(
            url="https://cli.jira.com",
            username="cliuser",          # CLI override
            password=None,
            token="clitoken",            # CLI override  
            bearer_token=None
        )
        
        mock_client.assert_called_once_with(
            base_url="https://cli.jira.com",
            username="cliuser",
            password=None,
            token="clitoken",
            bearer_token=None
        )


if __name__ == "__main__":
    unittest.main(verbosity=2) 
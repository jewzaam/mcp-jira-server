#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server CLI

This test module provides comprehensive coverage for the command line
interface functionality including argument parsing and configuration.
"""

import unittest
from unittest.mock import Mock, patch
import asyncio

# Import modules under test
from mcp_jira_server.config import ConfigError
from mcp_jira_server.server import main


class TestCLI(unittest.TestCase):
    """Test command line interface."""

    @patch("mcp_jira_server.server.load_config")
    @patch("mcp_jira_server.server.create_server")
    @patch("argparse.ArgumentParser.parse_args")
    def test_cli_01_parse_arguments_with_config_file_option(self, mock_parse, mock_create, mock_config):
        """CLI-01: Parse arguments with config file option."""
        mock_args = Mock()
        mock_args.config = "/path/to/config.yaml"
        mock_args.url = None
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {"url": "https://config.jira.com"}
        mock_server = Mock()
        mock_create.return_value = mock_server
        
        with patch.object(asyncio, 'run'):
            main()
        
        mock_config.assert_called_once_with("/path/to/config.yaml")

    @patch("mcp_jira_server.server.load_config")
    @patch("mcp_jira_server.server.create_server")
    @patch("argparse.ArgumentParser.parse_args")
    def test_cli_02_parse_arguments_with_all_authentication_options(self, mock_parse, mock_create, mock_config):
        """CLI-02: Parse arguments with all authentication options."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = "https://cli.jira.com"
        mock_args.username = "cliuser"
        mock_args.password = "clipass"
        mock_args.token = "clitoken"
        mock_args.bearer_token = "clibearer"
        mock_parse.return_value = mock_args
        mock_config.return_value = {}
        mock_server = Mock()
        mock_create.return_value = mock_server
        
        with patch.object(asyncio, 'run'):
            main()
        
        mock_create.assert_called_once_with(
            url="https://cli.jira.com",
            username="cliuser",
            password="clipass",
            token="clitoken",
            bearer_token="clibearer"
        )

    @patch("mcp_jira_server.server.load_config")
    @patch("argparse.ArgumentParser.parse_args")
    def test_cli_03_parse_arguments_with_required_url_parameter(self, mock_parse, mock_config):
        """CLI-03: Parse arguments with required URL parameter."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = "https://required.jira.com"
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {}
        
        with patch("mcp_jira_server.server.create_server") as mock_create:
            mock_server = Mock()
            mock_create.return_value = mock_server
            with patch.object(asyncio, 'run'):
                main()
        
        mock_create.assert_called_once()
        self.assertEqual(mock_create.call_args[1]["url"], "https://required.jira.com")

    @patch("mcp_jira_server.server.load_config")
    @patch("argparse.ArgumentParser.parse_args")
    def test_cli_04_handle_missing_url_requirement(self, mock_parse, mock_config):
        """CLI-04: Handle missing URL requirement."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = None
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {}
        
        with self.assertRaises(ConfigError):
            main()

    @patch("mcp_jira_server.server.load_config")
    @patch("mcp_jira_server.server.create_server")
    @patch("argparse.ArgumentParser.parse_args")
    def test_cli_05_cli_arguments_override_config_file_values(self, mock_parse, mock_create, mock_config):
        """CLI-05: CLI arguments override config file values."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = "https://override.jira.com"
        mock_args.username = "overrideuser"
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {
            "url": "https://config.jira.com",
            "username": "configuser",
            "token": "configtoken"
        }
        mock_server = Mock()
        mock_create.return_value = mock_server
        
        with patch.object(asyncio, 'run'):
            main()
        
        mock_create.assert_called_once_with(
            url="https://override.jira.com",  # CLI overrides config
            username="overrideuser",         # CLI overrides config
            password=None,
            token="configtoken",             # Config value used
            bearer_token=None
        )

    @patch("mcp_jira_server.server.load_config")
    @patch("argparse.ArgumentParser.parse_args")
    def test_cli_06_config_loading_with_explicit_path(self, mock_parse, mock_config):
        """CLI-06: Config loading with explicit path."""
        mock_args = Mock()
        mock_args.config = "/explicit/path/config.yaml"
        mock_args.url = None
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {"url": "https://explicit.jira.com"}
        
        with patch("mcp_jira_server.server.create_server") as mock_create:
            mock_server = Mock()
            mock_create.return_value = mock_server
            with patch.object(asyncio, 'run'):
                main()
        
        mock_config.assert_called_once_with("/explicit/path/config.yaml")

    @patch.dict("os.environ", {"MCP_JIRA_CONFIG": "/env/config.yaml"})
    @patch("mcp_jira_server.server.load_config")
    @patch("argparse.ArgumentParser.parse_args")
    def test_cli_07_config_loading_with_environment_variable(self, mock_parse, mock_config):
        """CLI-07: Config loading with environment variable."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = None
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {"url": "https://env.jira.com"}
        
        with patch("mcp_jira_server.server.create_server") as mock_create:
            mock_server = Mock()
            mock_create.return_value = mock_server
            with patch.object(asyncio, 'run'):
                main()
        
        mock_config.assert_called_once_with(None)

    @patch("mcp_jira_server.server.load_config")
    @patch("argparse.ArgumentParser.parse_args")
    def test_cli_08_config_loading_with_default_file_fallback(self, mock_parse, mock_config):
        """CLI-08: Config loading with default file fallback."""
        mock_args = Mock()
        mock_args.config = None
        mock_args.url = None
        mock_args.username = None
        mock_args.password = None
        mock_args.token = None
        mock_args.bearer_token = None
        mock_parse.return_value = mock_args
        mock_config.return_value = {"url": "https://default.jira.com"}
        
        with patch("mcp_jira_server.server.create_server") as mock_create:
            mock_server = Mock()
            mock_create.return_value = mock_server
            with patch.object(asyncio, 'run'):
                main()
        
        mock_config.assert_called_once_with(None)


if __name__ == "__main__":
    unittest.main(verbosity=2) 
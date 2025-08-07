#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Configuration

This test module provides comprehensive coverage for the configuration
loading functionality in the MCP JIRA server.
"""

import unittest
from unittest.mock import patch
import json
import yaml
import os
from pathlib import Path
from pyfakefs.fake_filesystem_unittest import TestCase

from mcp_jira_server.config import load_config, _load_from_file


class TestConfig(TestCase):
    """Test cases for configuration loading functionality."""

    def setUp(self):
        """Set up fake filesystem for each test."""
        self.setUpPyfakefs()

    def test_config_01_load_configuration_from_explicit_path(self):
        """CONFIG-01: Load configuration from explicit path."""
        config_data = {"url": "https://test.jira.com", "username": "testuser"}
        self.fs.create_file("/test/config.yaml", contents=yaml.dump(config_data))
        
        result = load_config("/test/config.yaml")
        self.assertEqual(result["url"], "https://test.jira.com")
        self.assertEqual(result["username"], "testuser")

    @patch("mcp_jira_server.config._load_from_file")
    def test_config_02_load_configuration_from_environment_variable(self, mock_load):
        """CONFIG-02: Load configuration from environment variable."""
        with patch.dict(os.environ, {"MCP_JIRA_CONFIG": "/test/config.yaml"}):
            load_config()
            mock_load.assert_called_once_with(Path("/test/config.yaml"))

    @patch("mcp_jira_server.config._load_from_file")
    def test_config_03_load_configuration_from_default_file(self, mock_load):
        """CONFIG-03: Load configuration from default file."""
        load_config()
        mock_load.assert_called_with(Path("mcp_jira_server.yaml"))

    def test_config_04_handle_missing_configuration_file_gracefully(self):
        """CONFIG-04: Handle missing configuration file gracefully."""
        # Don't create any files - they should be missing
        result = load_config("/nonexistent/config.yaml")
        self.assertEqual(result, {})

    def test_config_05_parse_yaml_configuration_correctly(self):
        """CONFIG-05: Parse YAML configuration correctly."""
        config_data = {"url": "https://yaml.jira.com", "username": "yamluser", "password": "yamlpass"}
        yaml_content = yaml.dump(config_data)
        self.fs.create_file("/test/config.yaml", contents=yaml_content)
        
        result = _load_from_file(Path("/test/config.yaml"))
        self.assertEqual(result["url"], "https://yaml.jira.com")
        self.assertEqual(result["username"], "yamluser")
        self.assertEqual(result["password"], "yamlpass")

    def test_config_06_parse_json_configuration_correctly(self):
        """CONFIG-06: Parse JSON configuration correctly."""
        config_data = {"url": "https://json.jira.com", "username": "jsonuser", "password": "jsonpass"}
        json_content = json.dumps(config_data)
        self.fs.create_file("/test/config.json", contents=json_content)
        
        result = _load_from_file(Path("/test/config.json"))
        self.assertEqual(result["url"], "https://json.jira.com")
        self.assertEqual(result["username"], "jsonuser")
        self.assertEqual(result["password"], "jsonpass")

    def test_config_07_handle_invalid_yaml_configuration(self):
        """CONFIG-07: Handle invalid YAML configuration."""
        invalid_yaml = "invalid: yaml: content: ["
        self.fs.create_file("/test/invalid.yaml", contents=invalid_yaml)
        
        with self.assertRaises(yaml.YAMLError):
            _load_from_file(Path("/test/invalid.yaml"))

    def test_config_08_handle_invalid_json_configuration(self):
        """CONFIG-08: Handle invalid JSON configuration."""
        invalid_json = '{"invalid": json content}'
        self.fs.create_file("/test/invalid.json", contents=invalid_json)
        
        with self.assertRaises(json.JSONDecodeError):
            _load_from_file(Path("/test/invalid.json"))

    def test_config_09_configuration_priority_order(self):
        """CONFIG-09: Configuration priority order (explicit > env > default)."""
        # Create default config file
        default_config = {"url": "https://default.jira.com", "username": "defaultuser"}
        self.fs.create_file("mcp_jira_server.yaml", contents=yaml.dump(default_config))
        
        # Create env config file
        env_config = {"url": "https://env.jira.com", "username": "envuser"}
        self.fs.create_file("env_config.yaml", contents=yaml.dump(env_config))
        
        # Create explicit config file
        explicit_config = {"url": "https://explicit.jira.com", "username": "explicituser"}
        self.fs.create_file("explicit_config.yaml", contents=yaml.dump(explicit_config))
        
        # Test explicit overrides both env and default
        with patch.dict(os.environ, {"MCP_JIRA_CONFIG": "env_config.yaml"}):
            result = load_config("explicit_config.yaml")
            self.assertEqual(result["url"], "https://explicit.jira.com")
            self.assertEqual(result["username"], "explicituser")

    def test_config_10_configuration_priority_order_env_over_default(self):
        """CONFIG-10: Configuration priority order (env > default)."""
        # Create default config file
        default_config = {"url": "https://default.jira.com", "username": "defaultuser"}
        self.fs.create_file("mcp_jira_server.yaml", contents=yaml.dump(default_config))
        
        # Create env config file  
        env_config = {"url": "https://env.jira.com", "username": "envuser"}
        self.fs.create_file("env_config.yaml", contents=yaml.dump(env_config))
        
        # Test env overrides default
        with patch.dict(os.environ, {"MCP_JIRA_CONFIG": "env_config.yaml"}):
            result = load_config()  # No explicit path
            self.assertEqual(result["url"], "https://env.jira.com")
            self.assertEqual(result["username"], "envuser")

    def test_config_11_configuration_priority_order_default_only(self):
        """CONFIG-11: Configuration priority order (default)."""
        # Create only default config file
        default_config = {"url": "https://default.jira.com", "username": "defaultuser"}
        self.fs.create_file("mcp_jira_server.yaml", contents=yaml.dump(default_config))
        
        # Test default is used when no env or explicit
        with patch.dict(os.environ, {}, clear=True):
            # Ensure MCP_JIRA_CONFIG is not set
            if "MCP_JIRA_CONFIG" in os.environ:
                del os.environ["MCP_JIRA_CONFIG"]
            result = load_config()  # No explicit path, no env
            self.assertEqual(result["url"], "https://default.jira.com")
            self.assertEqual(result["username"], "defaultuser")


if __name__ == "__main__":
    unittest.main(verbosity=2) 
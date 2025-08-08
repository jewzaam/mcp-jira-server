#!/usr/bin/env python3
"""Unit Tests for GET_ISSUE Functionality

Tests for the get_issue functionality based on TEST_PLAN_UNIT.md.
All tests follow TDD principles with mocked dependencies.
"""

import unittest
import tempfile
import os
import yaml
from unittest.mock import patch
from typing import Dict, Any

from mcp_jira_server.models import IssueDetails


class TestGetIssue(unittest.TestCase):
    """Test cases for GET_ISSUE functionality"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create temporary config file for tests
        self.config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.config_file.close()
        
        # Valid config for tests
        self.valid_config = {
            'jira': {
                'base_url': 'https://test-jira.example.com',
                'authentication': {
                    'type': 'bearer_token',
                    'token': 'test_token_value'
                },
                'projects': ['TEST', 'PROJ'],
                'sample_issues': {
                    'TEST': 'TEST-1',
                    'PROJ': 'PROJ-1'
                }
            }
        }

    def create_mock_issue_data(self, key: str, summary: str, status: str = "Open", include_parent: bool = False) -> Dict[str, Any]:
        """Helper to create mock JIRA issue data"""
        fields = {
            "summary": summary,
            "status": {"name": status},
            "issuetype": {"name": "Story"},
            "priority": {"name": "Medium"},
            "assignee": {
                "emailAddress": "test@example.com",
                "displayName": "Test User"
            },
            "reporter": {
                "emailAddress": "reporter@example.com",
                "displayName": "Reporter User"
            },
            "created": "2024-01-15T10:30:00.000Z",
            "updated": "2024-01-20T14:45:00.000Z",
            "description": "Test description"
        }
        
        if include_parent:
            fields["customfield_12313140"] = "EPIC-123"  # Epic Link
            fields["customfield_12311140"] = "PARENT-456"  # Parent Link
        
        return {
            "key": key,
            "self": f"https://test-jira.example.com/rest/api/2/issue/{key}",
            "fields": fields
        }

    def tearDown(self):
        """Clean up test fixtures after each test method"""
        # Clean up config file
        if os.path.exists(self.config_file.name):
            os.unlink(self.config_file.name)

    def test_get_issue_01_return_complete_issue_data_with_all_standard_fields(self):
        """GET_ISSUE-01: Return complete issue data with all standard fields"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_issue = self.create_mock_issue_data("TEST-123", "Test issue")
        
        with patch('mcp_jira_server.get_issue.make_jira_request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_issue
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_issue import get_issue
            
            load_config(self.config_file.name)
            
            # Act
            result = get_issue("TEST-123")
            
            # Assert
            assert isinstance(result, IssueDetails)
            assert result.key == "TEST-123"
            assert result.summary == "Test issue"
            assert result.status == "Open"
            assert result.type == "Story"
            assert result.priority == "Medium"
            assert result.assignee == "test@example.com"
            assert result.reporter == "reporter@example.com"
            assert result.created == "2024-01-15T10:30:00.000Z"
            assert result.updated == "2024-01-20T14:45:00.000Z"
            assert result.description == "Test description"
            assert result.raw == mock_issue
            
            # Verify API call
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert "rest/api/2/issue/TEST-123" in args[0]

    def test_get_issue_02_support_field_selection(self):
        """GET_ISSUE-02: Support field selection (key,summary,status,assignee)"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_issue = self.create_mock_issue_data("TEST-123", "Test issue")
        
        with patch('mcp_jira_server.get_issue.make_jira_request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_issue
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_issue import get_issue
            
            load_config(self.config_file.name)
            
            # Act
            get_issue("TEST-123", fields="key,summary,status,assignee")
            
            # Assert
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert kwargs["params"]["fields"] == "key,summary,status,assignee"

    def test_get_issue_03_include_parent_relationship_fields_in_raw_field(self):
        """GET_ISSUE-03: Include parent relationship fields in raw field"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_issue = self.create_mock_issue_data("TEST-123", "Test issue", include_parent=True)
        
        with patch('mcp_jira_server.get_issue.make_jira_request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_issue
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_issue import get_issue
            
            load_config(self.config_file.name)
            
            # Act
            result = get_issue("TEST-123")
            
            # Assert
            assert result.raw is not None
            assert result.raw["fields"]["customfield_12313140"] == "EPIC-123"
            assert result.raw["fields"]["customfield_12311140"] == "PARENT-456"

    def test_get_issue_04_consolidate_parent_fields_into_single_parent_key_response_field(self):
        """GET_ISSUE-04: Consolidate parent fields into single parent_key response field"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        # Test Parent Link takes precedence over Epic Link
        mock_issue = self.create_mock_issue_data("TEST-123", "Test issue", include_parent=True)
        
        with patch('mcp_jira_server.get_issue.make_jira_request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_issue
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_issue import get_issue
            
            load_config(self.config_file.name)
            
            # Act
            result = get_issue("TEST-123")
            
            # Assert
            assert result.parent_key == "PARENT-456"  # Parent Link takes precedence

    def test_get_issue_05_raw_field_contains_complete_jira_api_response(self):
        """GET_ISSUE-05: Raw field contains complete JIRA API response"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_issue = self.create_mock_issue_data("TEST-123", "Test issue")
        mock_issue["expand"] = "renderedFields,names,schema"
        mock_issue["fields"]["custom_field_example"] = "custom_value"
        
        with patch('mcp_jira_server.get_issue.make_jira_request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = mock_issue
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_issue import get_issue
            
            load_config(self.config_file.name)
            
            # Act
            result = get_issue("TEST-123")
            
            # Assert
            assert result.raw == mock_issue
            assert result.raw["expand"] == "renderedFields,names,schema"
            assert result.raw["fields"]["custom_field_example"] == "custom_value"

    def test_get_issue_06_fail_with_issue_not_found_error_for_non_existent_key(self):
        """GET_ISSUE-06: Fail with "Issue not found" error for non-existent key"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        with patch('mcp_jira_server.get_issue.make_jira_request') as mock_request:
            mock_request.return_value.status_code = 404
            mock_request.return_value.json.return_value = {
                "errorMessages": ["Issue does not exist or you do not have permission to see it."]
            }
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_issue import get_issue, IssueNotFoundError
            
            load_config(self.config_file.name)
            
            # Act & Assert
            with self.assertRaises(IssueNotFoundError) as context:
                get_issue("NONEXISTENT-999")
            
            assert "Issue not found" in str(context.exception)

    def test_get_issue_07_fail_with_permission_error_when_user_lacks_access(self):
        """GET_ISSUE-07: Fail with permission error when user lacks access"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        with patch('mcp_jira_server.get_issue.make_jira_request') as mock_request:
            mock_request.return_value.status_code = 403
            mock_request.return_value.json.return_value = {
                "errorMessages": ["You do not have permission to view this issue."]
            }
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_issue import get_issue, PermissionError
            
            load_config(self.config_file.name)
            
            # Act & Assert
            with self.assertRaises(PermissionError) as context:
                get_issue("SECRET-123")
            
            assert "permission" in str(context.exception).lower()

    def test_get_issue_08_fail_with_format_validation_error_for_invalid_issue_key_format(self):
        """GET_ISSUE-08: Fail with format validation error for invalid issue key format"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        from mcp_jira_server.config import load_config
        from mcp_jira_server.get_issue import get_issue, InvalidIssueKeyError
        
        load_config(self.config_file.name)
        
        # Act & Assert - Test various invalid formats
        invalid_keys = [
            "invalid",           # No dash
            "123-ABC",          # Number-letters instead of letters-number
            "PROJ",             # Missing number
            "123",              # Missing project
            "",                 # Empty string
            "PROJ-",            # Missing number after dash
            "-123",             # Missing project before dash
            "PROJ-ABC",         # Non-numeric issue number
        ]
        
        for invalid_key in invalid_keys:
            with self.subTest(key=invalid_key):
                with self.assertRaises(InvalidIssueKeyError):
                    get_issue(invalid_key)


if __name__ == "__main__":
    unittest.main()
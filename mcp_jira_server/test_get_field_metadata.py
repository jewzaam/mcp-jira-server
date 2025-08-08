#!/usr/bin/env python3
"""Unit Tests for GET_FIELD_METADATA Functionality

Tests for the get_field_metadata functionality based on TEST_PLAN_UNIT.md.
All tests follow TDD principles with mocked dependencies.
"""

import unittest
import tempfile
import os
import yaml
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from mcp_jira_server.models import FieldMetadata


class TestGetFieldMetadata(unittest.TestCase):
    """Test cases for GET_FIELD_METADATA functionality"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create temporary config file for tests
        self.config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.config_file.close()
        
        # Valid config for tests with pre-cached RFE project
        self.valid_config = {
            'jira': {
                'base_url': 'https://test-jira.example.com',
                'authentication': {
                    'type': 'bearer_token',
                    'token': 'test_token_value'
                },
                'projects': ['RFE', 'PROJ'],
                'sample_issues': {
                    'RFE': 'RFE-1',
                    'PROJ': 'PROJ-1'
                },
                'field_metadata_cache': {
                    'projects': [
                        {
                            'project_key': 'RFE',
                            'sample_issue': 'RFE-1'
                        }
                    ]
                }
            }
        }

    def create_mock_editmeta_response(self, include_parent_fields: bool = True) -> Dict[str, Any]:
        """Helper to create mock editmeta API response"""
        fields = {
            "summary": {
                "name": "Summary",
                "schema": {"type": "string"},
                "required": True
            },
            "description": {
                "name": "Description", 
                "schema": {"type": "string"},
                "required": False
            }
        }
        
        if include_parent_fields:
            fields.update({
                "customfield_12313140": {
                    "name": "Epic Link",
                    "schema": {
                        "type": "any",
                        "custom": "com.pyxis.greenhopper.jira:gh-epic-link"
                    },
                    "required": False
                },
                "customfield_12311140": {
                    "name": "Parent Link", 
                    "schema": {
                        "type": "any",
                        "custom": "com.atlassian.jira.plugin.system.customfieldtypes:issuelinks"
                    },
                    "required": False
                }
            })
        
        return {"fields": fields}

    def create_mock_issue_response(self, issue_type: str = "Feature Request") -> Dict[str, Any]:
        """Helper to create mock issue API response"""
        return {
            "fields": {
                "issuetype": {
                    "name": issue_type
                }
            }
        }

    def tearDown(self):
        """Clean up test fixtures after each test method"""
        # Clean up config file
        if os.path.exists(self.config_file.name):
            os.unlink(self.config_file.name)

    def test_field_meta_01_return_cached_metadata_for_pre_configured_project(self):
        """FIELD_META-01: Return cached metadata for pre-configured project (RFE)"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        # Mock the cache to have RFE data
        with patch('mcp_jira_server.config.get_cached_field_metadata') as mock_cache:
            mock_cache.return_value = [
                {
                    'id': 'customfield_12313140',
                    'name': 'Epic Link',
                    'schema': {'custom': 'com.pyxis.greenhopper.jira:gh-epic-link'},
                    'used_for_parent_key': True
                }
            ]
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata
            
            load_config(self.config_file.name)
            
            # Act
            result = get_field_metadata("RFE", issue_type="Feature Request")
            
            # Assert
            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(field, FieldMetadata) for field in result)
            # Verify Epic Link field is marked as parent key field
            epic_link = next((f for f in result if f.name == "Epic Link"), None)
            assert epic_link is not None
            assert epic_link.used_for_parent_key is True

    def test_field_meta_02_discover_and_cache_metadata_using_sample_issue(self):
        """FIELD_META-02: Discover and cache metadata using sample issue"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_editmeta = self.create_mock_editmeta_response()
        mock_issue = self.create_mock_issue_response()
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            # Mock editmeta call
            def mock_request_side_effect(path, params=None):
                response = MagicMock()
                response.status_code = 200
                if "editmeta" in path:
                    response.json.return_value = mock_editmeta
                else:  # issue call
                    response.json.return_value = mock_issue
                return response
            
            mock_request.side_effect = mock_request_side_effect
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata
            
            load_config(self.config_file.name)
            
            # Act
            result = get_field_metadata("NEWPROJ", "NEWPROJ-123")
            
            # Assert
            assert isinstance(result, list)
            assert len(result) > 0
            # Verify editmeta API was called
            mock_request.assert_any_call("rest/api/2/issue/NEWPROJ-123/editmeta")

    def test_field_meta_03_fail_when_no_sample_issue_provided_and_no_cached_data_exists(self):
        """FIELD_META-03: Fail when no sample_issue provided and no cached data exists"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        # Mock cache to return None (no cached data)
        with patch('mcp_jira_server.config.get_cached_field_metadata') as mock_cache:
            mock_cache.return_value = None
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata
            
            load_config(self.config_file.name)
            
            # Act & Assert
            with self.assertRaises(Exception) as context:
                get_field_metadata("UNCACHED", issue_type="Story")
            
            assert "no cached metadata found" in str(context.exception).lower()

    def test_field_meta_04_mark_fields_matching_link_pattern_as_used_for_parent_key_true(self):
        """FIELD_META-04: Mark fields matching .*Link pattern as used_for_parent_key: true"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_editmeta = {
            "fields": {
                "customfield_12313140": {
                    "name": "Epic Link",
                    "schema": {"type": "any", "custom": "com.pyxis.greenhopper.jira:gh-epic-link"},
                    "required": False
                },
                "customfield_12311140": {
                    "name": "Parent Link",
                    "schema": {"type": "any", "custom": "com.atlassian.jira.plugin.system.customfieldtypes:issuelinks"},
                    "required": False
                },
                "customfield_12345678": {
                    "name": "Feature Link",
                    "schema": {"type": "any"},
                    "required": False
                }
            }
        }
        mock_issue = self.create_mock_issue_response()
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            def mock_request_side_effect(path, params=None):
                response = MagicMock()
                response.status_code = 200
                if "editmeta" in path:
                    response.json.return_value = mock_editmeta
                else:
                    response.json.return_value = mock_issue
                return response
            
            mock_request.side_effect = mock_request_side_effect
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata
            
            load_config(self.config_file.name)
            
            # Act
            result = get_field_metadata("TEST", "TEST-123")
            
            # Assert
            link_fields = [f for f in result if "Link" in f.name]
            assert len(link_fields) >= 3  # Epic Link, Parent Link, Feature Link
            for field in link_fields:
                assert field.used_for_parent_key is True

    def test_field_meta_05_mark_non_link_fields_as_used_for_parent_key_false(self):
        """FIELD_META-05: Mark non-link fields as used_for_parent_key: false"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_editmeta = self.create_mock_editmeta_response()
        mock_issue = self.create_mock_issue_response()
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            def mock_request_side_effect(path, params=None):
                response = MagicMock()
                response.status_code = 200
                if "editmeta" in path:
                    response.json.return_value = mock_editmeta
                else:
                    response.json.return_value = mock_issue
                return response
            
            mock_request.side_effect = mock_request_side_effect
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata
            
            load_config(self.config_file.name)
            
            # Act
            result = get_field_metadata("TEST", "TEST-123")
            
            # Assert
            non_link_fields = [f for f in result if "Link" not in f.name]
            assert len(non_link_fields) >= 2  # Summary, Description
            for field in non_link_fields:
                assert field.used_for_parent_key is False

    def test_field_meta_06_include_field_type_description_and_requirement_status(self):
        """FIELD_META-06: Include field type, description, and requirement status"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_editmeta = {
            "fields": {
                "summary": {
                    "name": "Summary",
                    "schema": {"type": "string"},
                    "required": True,
                    "operations": ["set"]
                }
            }
        }
        mock_issue = self.create_mock_issue_response()
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            def mock_request_side_effect(path, params=None):
                response = MagicMock()
                response.status_code = 200
                if "editmeta" in path:
                    response.json.return_value = mock_editmeta
                else:
                    response.json.return_value = mock_issue
                return response
            
            mock_request.side_effect = mock_request_side_effect
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata
            
            load_config(self.config_file.name)
            
            # Act
            result = get_field_metadata("TEST", "TEST-123")
            
            # Assert
            summary_field = next((f for f in result if f.name == "Summary"), None)
            assert summary_field is not None
            assert summary_field.type == "string"
            assert summary_field.required is True
            assert summary_field.custom is False

    def test_field_meta_07_use_editmeta_api_for_field_discovery(self):
        """FIELD_META-07: Use editmeta API for field discovery"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_editmeta = self.create_mock_editmeta_response()
        mock_issue = self.create_mock_issue_response()
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            def mock_request_side_effect(path, params=None):
                response = MagicMock()
                response.status_code = 200
                if "editmeta" in path:
                    response.json.return_value = mock_editmeta
                else:
                    response.json.return_value = mock_issue
                return response
            
            mock_request.side_effect = mock_request_side_effect
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata
            
            load_config(self.config_file.name)
            
            # Act
            get_field_metadata("TEST", "TEST-123")
            
            # Assert
            mock_request.assert_any_call("rest/api/2/issue/TEST-123/editmeta")

    def test_field_meta_08_cache_discovered_metadata_for_future_use(self):
        """FIELD_META-08: Cache discovered metadata for future use"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        mock_editmeta = self.create_mock_editmeta_response()
        mock_issue = self.create_mock_issue_response()
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            with patch('mcp_jira_server.config._field_cache', {}) as mock_cache:
                def mock_request_side_effect(path, params=None):
                    response = MagicMock()
                    response.status_code = 200
                    if "editmeta" in path:
                        response.json.return_value = mock_editmeta
                    else:
                        response.json.return_value = mock_issue
                    return response
                
                mock_request.side_effect = mock_request_side_effect
                
                from mcp_jira_server.config import load_config
                from mcp_jira_server.get_field_metadata import get_field_metadata
                
                load_config(self.config_file.name)
                
                # Act
                get_field_metadata("TEST", "TEST-123")
                
                # Assert - verify cache was populated
                assert "TEST::Feature Request" in mock_cache

    def test_field_meta_09_fail_with_project_not_found_error_for_non_existent_project(self):
        """FIELD_META-09: Fail with "Project not found" error for non-existent project"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            # Mock editmeta call to return 404 for project not found
            response = MagicMock()
            response.status_code = 404
            response.json.return_value = {"errorMessages": ["Project does not exist"]}
            mock_request.return_value = response
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata, ProjectNotFoundError
            
            load_config(self.config_file.name)
            
            # Act & Assert
            with self.assertRaises(ProjectNotFoundError) as context:
                get_field_metadata("NONEXISTENT", "NONEXISTENT-123")
            
            assert "project not found" in str(context.exception).lower()

    def test_field_meta_10_fail_with_sample_issue_not_found_error_for_non_existent_sample(self):
        """FIELD_META-10: Fail with "Sample issue not found" error for non-existent sample"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            # Mock editmeta call to return 404 for issue not found
            response = MagicMock()
            response.status_code = 404
            response.json.return_value = {"errorMessages": ["Issue does not exist"]}
            mock_request.return_value = response
            
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata, SampleIssueNotFoundError
            
            load_config(self.config_file.name)
            
            # Act & Assert
            with self.assertRaises(SampleIssueNotFoundError) as context:
                get_field_metadata("TEST", "NONEXISTENT-999")
            
            assert "sample issue not found" in str(context.exception).lower()

    def test_field_meta_11_fail_with_permission_error_for_insufficient_editmeta_access(self):
        """FIELD_META-11: Fail with permission error for insufficient editmeta access"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            # Mock editmeta call to return 403 for permission denied
            response = MagicMock()
            response.status_code = 403
            response.json.return_value = {"errorMessages": ["You do not have permission"]}
            mock_request.return_value = response

            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata

            load_config(self.config_file.name)

            # Act & Assert
            with self.assertRaises(Exception) as context:
                get_field_metadata("TEST", "TEST-123")

            assert "permission" in str(context.exception).lower()

    def test_field_meta_12_cache_only_lookup_with_issue_type_returns_metadata(self):
        """FIELD_META-12: Cache-only lookup with issue_type parameter returns cached metadata"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        # Mock the cache to have data
        with patch('mcp_jira_server.config.get_cached_field_metadata') as mock_cache:
            mock_cache.return_value = [
                {
                    'id': 'customfield_12313140',
                    'name': 'Epic Link',
                    'schema': {'custom': 'com.pyxis.greenhopper.jira:gh-epic-link'},
                    'used_for_parent_key': True
                }
            ]

            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata

            load_config(self.config_file.name)

            # Act
            result = get_field_metadata("TEST", issue_type="Story")

            # Assert
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].name == "Epic Link"
            assert result[0].used_for_parent_key is True

    def test_field_meta_13_cache_only_lookup_fails_when_no_cached_data(self):
        """FIELD_META-13: Cache-only lookup fails when no cached data exists for issue_type"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        # Mock cache to return None (no cached data)
        with patch('mcp_jira_server.config.get_cached_field_metadata') as mock_cache:
            mock_cache.return_value = None

            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_field_metadata

            load_config(self.config_file.name)

            # Act & Assert
            with self.assertRaises(Exception) as context:
                get_field_metadata("TEST", issue_type="Story")

            assert "No cached metadata found for TEST::Story" in str(context.exception)

    def test_field_meta_14_fail_when_both_sample_issue_and_issue_type_provided(self):
        """FIELD_META-14: Fail when both sample_issue and issue_type are provided"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        from mcp_jira_server.config import load_config
        from mcp_jira_server.get_field_metadata import get_field_metadata

        load_config(self.config_file.name)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            get_field_metadata("TEST", sample_issue="TEST-123", issue_type="Story")

        assert "Cannot provide both sample_issue and issue_type parameters" in str(context.exception)

    def test_field_meta_15_fail_when_neither_sample_issue_nor_issue_type_provided(self):
        """FIELD_META-15: Fail when neither sample_issue nor issue_type are provided"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        from mcp_jira_server.config import load_config
        from mcp_jira_server.get_field_metadata import get_field_metadata

        load_config(self.config_file.name)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            get_field_metadata("TEST")

        assert "Must provide either sample_issue or issue_type parameter" in str(context.exception)

    def test_field_meta_16_no_api_calls_made_when_using_issue_type(self):
        """FIELD_META-16: No JIRA API calls made when using issue_type parameter"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        # Mock cache to have data
        with patch('mcp_jira_server.config.get_cached_field_metadata') as mock_cache:
            with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
                mock_cache.return_value = [
                    {
                        'id': 'customfield_12313140',
                        'name': 'Epic Link',
                        'schema': {'custom': 'com.pyxis.greenhopper.jira:gh-epic-link'}
                    }
                ]

                from mcp_jira_server.config import load_config
                from mcp_jira_server.get_field_metadata import get_field_metadata

                load_config(self.config_file.name)

                # Act
                get_field_metadata("TEST", issue_type="Story")

                # Assert - no API calls should have been made
                mock_request.assert_not_called()

    def test_known_parent_fields_01_return_all_unique_field_ids_across_cache(self):
        """KNOWN_PARENT_FIELDS-01: Return all unique parent field IDs across all cached projects/issue types"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        # Mock cache with multiple project::issue_type combinations
        mock_cache_data = {
            "PROJ1::Story": [
                {
                    'id': 'customfield_12313140',
                    'name': 'Epic Link',
                    'schema': {'custom': 'com.pyxis.greenhopper.jira:gh-epic-link'},
                    'used_for_parent_key': True
                }
            ],
            "PROJ2::Bug": [
                {
                    'id': 'customfield_12311140',
                    'name': 'Parent Link',
                    'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:issuelinks'},
                    'used_for_parent_key': True
                },
                {
                    'id': 'customfield_12345678',
                    'name': 'Feature Link',
                    'schema': {},
                    'used_for_parent_key': True
                }
            ]
        }

        with patch('mcp_jira_server.config._field_cache', mock_cache_data):
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_known_parent_fields

            load_config(self.config_file.name)

            # Act
            result = get_known_parent_fields()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 3
            assert "customfield_12313140" in result
            assert "customfield_12311140" in result
            assert "customfield_12345678" in result

    def test_known_parent_fields_02_return_empty_array_when_no_cache(self):
        """KNOWN_PARENT_FIELDS-02: Return empty array when no cached field metadata exists"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        # Mock empty cache
        with patch('mcp_jira_server.config._field_cache', {}):
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_known_parent_fields

            load_config(self.config_file.name)

            # Act
            result = get_known_parent_fields()

            # Assert
            assert isinstance(result, list)
            assert len(result) == 0

    def test_known_parent_fields_03_return_only_parent_key_field_ids(self):
        """KNOWN_PARENT_FIELDS-03: Return only field IDs where used_for_parent_key is true"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        # Mock cache with mixed field types - only Link fields should be returned
        mock_cache_data = {
            "PROJ::Story": [
                {
                    'id': 'customfield_12313140',
                    'name': 'Epic Link',
                    'schema': {'custom': 'com.pyxis.greenhopper.jira:gh-epic-link'},
                    'used_for_parent_key': True
                },
                {
                    'id': 'summary',
                    'name': 'Summary',
                    'schema': {'type': 'string'},
                    'used_for_parent_key': False
                },
                {
                    'id': 'customfield_12311140',
                    'name': 'Parent Link',
                    'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:issuelinks'},
                    'used_for_parent_key': True
                }
            ]
        }

        with patch('mcp_jira_server.config._field_cache', mock_cache_data):
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_known_parent_fields

            load_config(self.config_file.name)

            # Act
            result = get_known_parent_fields()

            # Assert - only parent field IDs, not summary
            assert isinstance(result, list)
            assert len(result) == 2
            assert "customfield_12313140" in result
            assert "customfield_12311140" in result
            assert "summary" not in result

    def test_known_parent_fields_04_deduplicate_field_ids_across_combinations(self):
        """KNOWN_PARENT_FIELDS-04: Deduplicate field IDs across multiple project::issue_type combinations"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        # Mock cache with duplicate field IDs across different project::issue_type combinations
        mock_cache_data = {
            "PROJ1::Story": [
                {
                    'id': 'customfield_12313140',
                    'name': 'Epic Link',
                    'schema': {'custom': 'com.pyxis.greenhopper.jira:gh-epic-link'},
                    'used_for_parent_key': True
                }
            ],
            "PROJ1::Bug": [
                {
                    'id': 'customfield_12313140',  # Same field ID as above
                    'name': 'Epic Link',
                    'schema': {'custom': 'com.pyxis.greenhopper.jira:gh-epic-link'},
                    'used_for_parent_key': True
                }
            ],
            "PROJ2::Feature": [
                {
                    'id': 'customfield_12311140',
                    'name': 'Parent Link',
                    'schema': {'custom': 'com.atlassian.jira.plugin.system.customfieldtypes:issuelinks'},
                    'used_for_parent_key': True
                }
            ]
        }

        with patch('mcp_jira_server.config._field_cache', mock_cache_data):
            from mcp_jira_server.config import load_config
            from mcp_jira_server.get_field_metadata import get_known_parent_fields

            load_config(self.config_file.name)

            # Act
            result = get_known_parent_fields()

            # Assert - should deduplicate the Epic Link field
            assert isinstance(result, list)
            assert len(result) == 2  # Only 2 unique field IDs
            assert "customfield_12313140" in result
            assert "customfield_12311140" in result

    def test_known_parent_fields_05_no_api_calls_made(self):
        """KNOWN_PARENT_FIELDS-05: No JIRA API calls are made (cache-only operation)"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)

        # Mock cache and API request
        mock_cache_data = {
            "PROJ::Story": [
                {
                    'id': 'customfield_12313140',
                    'name': 'Epic Link',
                    'schema': {'custom': 'com.pyxis.greenhopper.jira:gh-epic-link'}
                }
            ]
        }

        with patch('mcp_jira_server.config._field_cache', mock_cache_data):
            with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
                from mcp_jira_server.config import load_config
                from mcp_jira_server.get_field_metadata import get_known_parent_fields

                load_config(self.config_file.name)

                # Act
                get_known_parent_fields()

                # Assert - no API calls should have been made
                mock_request.assert_not_called()

    def test_field_meta_cache_stores_all_fields_not_just_parent_fields(self):
        """Verify that get_field_metadata caches ALL discovered fields, not just parent fields"""
        # Arrange
        with open(self.config_file.name, 'w') as f:
            yaml.dump(self.valid_config, f)
        
        # Create mock editmeta with both parent and non-parent fields
        mock_editmeta = {
            "fields": {
                "summary": {
                    "name": "Summary",
                    "schema": {"type": "string"},
                    "required": True
                },
                "description": {
                    "name": "Description", 
                    "schema": {"type": "string"},
                    "required": False
                },
                "customfield_12313140": {
                    "name": "Epic Link",
                    "schema": {"type": "any", "custom": "com.pyxis.greenhopper.jira:gh-epic-link"},
                    "required": False
                },
                "customfield_12311140": {
                    "name": "Parent Link",
                    "schema": {"type": "any", "custom": "com.atlassian.jira.plugin.system.customfieldtypes:issuelinks"},
                    "required": False
                }
            }
        }
        mock_issue = self.create_mock_issue_response()
        
        with patch('mcp_jira_server.get_field_metadata.make_jira_request') as mock_request:
            def mock_request_side_effect(path, params=None):
                response = MagicMock()
                response.status_code = 200
                if "editmeta" in path:
                    response.json.return_value = mock_editmeta
                else:
                    response.json.return_value = mock_issue
                return response
            
            mock_request.side_effect = mock_request_side_effect
            
            from mcp_jira_server.config import load_config, _field_cache
            from mcp_jira_server.get_field_metadata import get_field_metadata
            
            load_config(self.config_file.name)
            
            # Clear cache to ensure clean test
            _field_cache.clear()
            
            # Act
            result = get_field_metadata("TEST", sample_issue="TEST-123")
            
            # Assert
            cache_key = "TEST::Feature Request"
            assert cache_key in _field_cache, f"Cache should contain key {cache_key}"
            
            cached_fields = _field_cache[cache_key]
            
            # Verify ALL 4 fields are cached (2 parent + 2 non-parent)
            assert len(cached_fields) == 4, f"Expected 4 cached fields, got {len(cached_fields)}"
            
            # Find fields by ID
            cached_field_ids = {field['id'] for field in cached_fields}
            expected_field_ids = {"summary", "description", "customfield_12313140", "customfield_12311140"}
            assert cached_field_ids == expected_field_ids, f"Expected {expected_field_ids}, got {cached_field_ids}"
            
            # Verify parent field flags are correctly set
            for field in cached_fields:
                if field['id'] in ['customfield_12313140', 'customfield_12311140']:
                    assert field['used_for_parent_key'] is True, f"Field {field['id']} should be marked as parent field"
                else:
                    assert field['used_for_parent_key'] is False, f"Field {field['id']} should NOT be marked as parent field"
            
            # Verify returned result also contains all fields
            assert len(result) == 4, f"Expected 4 returned fields, got {len(result)}"
            returned_field_ids = {field.id for field in result}
            assert returned_field_ids == expected_field_ids, f"Expected {expected_field_ids}, got {returned_field_ids}"


if __name__ == "__main__":
    unittest.main()
#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Data Models

This test module provides comprehensive coverage for Pydantic data model
validation used by the MCP JIRA server.

Test IDs: MODELS-01 through MODELS-07
"""

import unittest

# Import modules under test
from mcp_jira_server.server import IssueSummary, IssueDetails


class TestModels(unittest.TestCase):
    """Test data model validation."""

    def test_models_01_issue_summary_model_validation(self):
        """MODELS-01: IssueSummary model validation."""
        summary = IssueSummary(
            key="TEST-123",
            summary="Test summary",
            status="Open",
            url="https://test.jira.com/browse/TEST-123"
        )
        
        self.assertEqual(summary.key, "TEST-123")
        self.assertEqual(summary.summary, "Test summary")
        self.assertEqual(summary.status, "Open")
        self.assertEqual(summary.url, "https://test.jira.com/browse/TEST-123")

    def test_models_02_issue_summary_model_with_all_required_fields(self):
        """MODELS-02: IssueSummary model with all required fields."""
        data = {
            "key": "REQ-456",
            "summary": "Required fields test",
            "status": "Done",
            "url": "https://test.jira.com/browse/REQ-456"
        }
        
        summary = IssueSummary(**data)
        self.assertIsInstance(summary, IssueSummary)

    def test_models_03_issue_summary_model_ignores_extra_fields(self):
        """MODELS-03: IssueSummary model ignores extra fields."""
        data = {
            "key": "EXTRA-789",
            "summary": "Extra fields test",
            "status": "In Progress",
            "url": "https://test.jira.com/browse/EXTRA-789",
            "extra_field": "should be ignored",
            "another_extra": 123
        }
        
        summary = IssueSummary(**data)
        self.assertEqual(summary.key, "EXTRA-789")
        # Extra fields should not cause errors

    def test_models_04_issue_details_model_validation(self):
        """MODELS-04: IssueDetails model validation."""
        details = IssueDetails(
            key="DETAIL-123",
            summary="Details test",
            description="Test description",
            status="Open",
            raw={"key": "DETAIL-123", "fields": {}}
        )
        
        self.assertEqual(details.key, "DETAIL-123")
        self.assertEqual(details.description, "Test description")

    def test_models_05_issue_details_model_with_optional_description(self):
        """MODELS-05: IssueDetails model with optional description."""
        details = IssueDetails(
            key="OPT-456",
            summary="Optional description test",
            description="Has description",
            status="Done",
            raw={}
        )
        
        self.assertEqual(details.description, "Has description")

    def test_models_06_issue_details_model_with_none_description(self):
        """MODELS-06: IssueDetails model with None description."""
        details = IssueDetails(
            key="NONE-789",
            summary="None description test",
            description=None,
            status="Closed",
            raw={}
        )
        
        self.assertIsNone(details.description)

    def test_models_07_issue_details_model_includes_raw_field(self):
        """MODELS-07: IssueDetails model includes raw field."""
        raw_data = {
            "key": "RAW-123",
            "fields": {
                "summary": "Raw data test",
                "custom_field": "custom_value"
            }
        }
        
        details = IssueDetails(
            key="RAW-123",
            summary="Raw data test",
            description=None,
            status="Open",
            raw=raw_data
        )
        
        self.assertEqual(details.raw, raw_data)
        self.assertIn("custom_field", details.raw["fields"])


if __name__ == "__main__":
    unittest.main(verbosity=2) 
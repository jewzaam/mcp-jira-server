#!/usr/bin/env python3
"""Unit tests for MCP JIRA Server Tools

This test module provides comprehensive coverage for the MCP tools
functionality including search_issues, get_issue, and identifier_hint.
"""

import unittest
from unittest.mock import Mock, patch
import asyncio

# Import modules under test  
from mcp_jira_server.server import (
    JiraTools, IssueSummary, IssueDetails, IssueRelationships, 
    IssueLink, ParentInfo, AncestorTree
)


class TestTools(unittest.TestCase):
    """Test MCP tool implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client.base_url = "https://test.jira.com"
        self.mock_client.api_base = "https://test.jira.com/rest/api/2"
        self.tools = JiraTools(self.mock_client)

    def test_tools_01_search_issues_with_simple_text_query(self):
        """TOOLS-01: Search issues with simple text query."""
        self.mock_client._make_api_request.return_value = {
            "issues": [{
                "key": "TEST-123",
                "fields": {
                    "summary": "Test issue",
                    "status": {"name": "Open"}
                }
            }]
        }
        
        result = asyncio.run(self.tools.search_issues("simple search"))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].key, "TEST-123")
        self.assertEqual(result[0].summary, "Test issue")
        self.assertEqual(result[0].status, "Open")

    def test_tools_02_search_issues_with_jql_query(self):
        """TOOLS-02: Search issues with JQL query."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        asyncio.run(self.tools.search_issues("project = TEST AND status = Open"))
        
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertIn("jql", kwargs["params"])
        self.assertEqual(kwargs["params"]["jql"], "project = TEST AND status = Open")

    def test_tools_03_search_issues_with_jql_detection_equals_sign(self):
        """TOOLS-03: Search issues with JQL detection (equals sign)."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        asyncio.run(self.tools.search_issues("project = TEST"))
        
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["jql"], "project = TEST")

    def test_tools_04_search_issues_with_jql_detection_and_or_operators(self):
        """TOOLS-04: Search issues with JQL detection (AND/OR operators)."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        asyncio.run(self.tools.search_issues("status = Open AND assignee = currentUser()"))
        
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["jql"], "status = Open AND assignee = currentUser()")

    def test_tools_05_search_issues_with_max_results_parameter(self):
        """TOOLS-05: Search issues with max results parameter."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        asyncio.run(self.tools.search_issues("test", max_results=50))
        
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["maxResults"], 50)

    def test_tools_06_search_issues_with_max_results_boundary(self):
        """TOOLS-06: Search issues with max results boundary (1-100)."""
        self.mock_client._make_api_request.return_value = {"issues": []}
        
        # Test lower boundary
        asyncio.run(self.tools.search_issues("test", max_results=0))
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["maxResults"], 1)
        
        # Test upper boundary
        asyncio.run(self.tools.search_issues("test", max_results=150))
        args, kwargs = self.mock_client._make_api_request.call_args
        self.assertEqual(kwargs["params"]["maxResults"], 100)

    def test_tools_07_search_issues_returns_proper_issue_summary_objects(self):
        """TOOLS-07: Search issues returns proper IssueSummary objects."""
        self.mock_client._make_api_request.return_value = {
            "issues": [{
                "key": "TEST-456",
                "fields": {
                    "summary": "Another test issue",
                    "status": {"name": "In Progress"}
                }
            }]
        }
        
        result = asyncio.run(self.tools.search_issues("test"))
        
        self.assertIsInstance(result[0], IssueSummary)
        self.assertEqual(result[0].url, "https://test.jira.com/browse/TEST-456")

    def test_tools_08_get_single_issue_by_key(self):
        """TOOLS-08: Get single issue by key."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-789",
            "fields": {
                "summary": "Single issue test",
                "description": "Test description",
                "status": {"name": "Done"}
            }
        }
        
        result = asyncio.run(self.tools.get_issue("TEST-789"))
        
        self.mock_client.get_issue.assert_called_once_with("TEST-789", expand=None)
        self.assertEqual(result.key, "TEST-789")
        self.assertEqual(result.summary, "Single issue test")
        self.assertEqual(result.description, "Test description")
        self.assertEqual(result.status, "Done")

    def test_tools_09_get_issue_with_expand_parameter(self):
        """TOOLS-09: Get issue with expand parameter."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-999",
            "fields": {
                "summary": "Expanded issue",
                "status": {"name": "Open"}
            }
        }
        
        asyncio.run(self.tools.get_issue("TEST-999", expand="changelog,comments"))
        
        self.mock_client.get_issue.assert_called_once_with("TEST-999", expand="changelog,comments")

    def test_tools_10_get_issue_returns_proper_issue_details_object(self):
        """TOOLS-10: Get issue returns proper IssueDetails object."""
        issue_data = {
            "key": "TEST-111",
            "fields": {
                "summary": "Details test",
                "description": None,
                "status": {"name": "Closed"}
            }
        }
        self.mock_client.get_issue.return_value = issue_data
        
        result = asyncio.run(self.tools.get_issue("TEST-111"))
        
        self.assertIsInstance(result, IssueDetails)
        self.assertEqual(result.description, None)
        self.assertEqual(result.raw, issue_data)

    def test_tools_11_identifier_hint_returns_expected_format_description(self):
        """TOOLS-11: Identifier hint returns expected format description."""
        result = asyncio.run(self.tools.identifier_hint())
        
        self.assertIn("PROJECT>-<NUMBER>", result)
        self.assertIn("RFE-7877", result)

    def test_tools_12_get_issue_relationships_with_all_types(self):
        """TOOLS-12: Get issue relationships with all relationship types."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-100",
            "fields": {
                "parent": {"key": "TEST-99"},
                "subtasks": [
                    {"key": "TEST-101", "fields": {"summary": "Subtask 1", "status": {"name": "Open"}}},
                    {"key": "TEST-102", "fields": {"summary": "Subtask 2", "status": {"name": "Done"}}}
                ],
                "issuelinks": [
                    {
                        "type": {"name": "Blocks", "inward": "is blocked by", "outward": "blocks"},
                        "inwardIssue": {"key": "TEST-50"}
                    },
                    {
                        "type": {"name": "Depends", "inward": "depends on", "outward": "is depended on by"},
                        "outwardIssue": {"key": "TEST-200"}
                    }
                ]
            }
        }
        self.mock_client.get_remote_links.return_value = [{"id": "1"}, {"id": "2"}]
        
        result = asyncio.run(self.tools.get_issue_relationships("TEST-100"))
        
        self.assertIsInstance(result, IssueRelationships)
        self.assertEqual(result.issue_key, "TEST-100")
        self.assertEqual(result.parent, "TEST-99")
        self.assertEqual(len(result.subtasks), 2)
        self.assertIn("TEST-101", result.subtasks)
        self.assertIn("TEST-102", result.subtasks)
        self.assertEqual(len(result.issue_links), 2)
        self.assertEqual(result.remote_links_count, 2)

    def test_tools_13_get_issue_relationships_with_no_relationships(self):
        """TOOLS-13: Get issue relationships with no relationships."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-SOLO",
            "fields": {
                "subtasks": [],
                "issuelinks": []
            }
        }
        self.mock_client.get_remote_links.return_value = []
        
        result = asyncio.run(self.tools.get_issue_relationships("TEST-SOLO"))
        
        self.assertEqual(result.parent, None)
        self.assertEqual(len(result.subtasks), 0)
        self.assertEqual(len(result.issue_links), 0)
        self.assertEqual(result.remote_links_count, 0)

    def test_tools_14_get_issue_relationships_link_parsing(self):
        """TOOLS-14: Get issue relationships link parsing."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-LINK",
            "fields": {
                "subtasks": [],
                "issuelinks": [
                    {
                        "type": {"name": "Blocks", "inward": "is blocked by", "outward": "blocks"},
                        "inwardIssue": {"key": "TEST-IN"}
                    },
                    {
                        "type": {"name": "Relates", "inward": "relates to", "outward": "relates to"},
                        "outwardIssue": {"key": "TEST-OUT"}
                    }
                ]
            }
        }
        self.mock_client.get_remote_links.return_value = []
        
        result = asyncio.run(self.tools.get_issue_relationships("TEST-LINK"))
        
        # Check inward link
        inward_link = next(link for link in result.issue_links if link.direction == "inward")
        self.assertIsInstance(inward_link, IssueLink)
        self.assertEqual(inward_link.issue_key, "TEST-IN")
        self.assertEqual(inward_link.link_type, "Blocks")
        self.assertEqual(inward_link.relationship, "is blocked by")
        
        # Check outward link
        outward_link = next(link for link in result.issue_links if link.direction == "outward")
        self.assertEqual(outward_link.issue_key, "TEST-OUT")
        self.assertEqual(outward_link.link_type, "Relates")
        self.assertEqual(outward_link.relationship, "relates to")

    def test_tools_18_get_children_with_subtasks_only(self):
        """TOOLS-18: Get children with subtasks only."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-PARENT",
            "fields": {
                "subtasks": [
                    {
                        "key": "TEST-SUB1",
                        "fields": {"summary": "Subtask 1", "status": {"name": "Open"}}
                    },
                    {
                        "key": "TEST-SUB2", 
                        "fields": {"summary": "Subtask 2", "status": {"name": "Done"}}
                    }
                ]
            }
        }
        
        result = asyncio.run(self.tools.get_children("TEST-PARENT", include_parent_links=False))
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].key, "TEST-SUB1")
        self.assertEqual(result[1].key, "TEST-SUB2")
        self.assertIsInstance(result[0], IssueSummary)

    def test_tools_18b_get_children_default_behavior(self):
        """TOOLS-18B: Get children with default behavior (includes both subtasks and parent links)."""
        self.mock_client.get_issue.side_effect = [
            # First call for getting subtasks
            {
                "key": "TEST-PARENT",
                "fields": {
                    "subtasks": [
                        {
                            "key": "TEST-SUB1",
                            "fields": {"summary": "Subtask 1", "status": {"name": "Open"}}
                        }
                    ]
                }
            },
            # Second call for parent-link child
            {"key": "TEST-PCHILD1", "fields": {"summary": "Parent Child 1", "status": {"name": "Open"}}}
        ]
        self.mock_client.get_parent_link_children.return_value = ["TEST-PCHILD1"]
        
        result = asyncio.run(self.tools.get_children("TEST-PARENT"))
        
        # Should get both subtasks and parent-link children
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].key, "TEST-SUB1")
        self.assertEqual(result[1].key, "TEST-PCHILD1")
        self.mock_client.get_parent_link_children.assert_called_once_with("TEST-PARENT", "Parent Link")

    def test_tools_19_get_children_with_parent_links(self):
        """TOOLS-19: Get children with parent links enabled."""
        self.mock_client.get_issue.side_effect = [
            # First call for getting subtasks
            {"key": "TEST-PARENT", "fields": {"subtasks": []}},
            # Subsequent calls for parent-link children
            {"key": "TEST-PCHILD1", "fields": {"summary": "Parent Child 1", "status": {"name": "Open"}}},
            {"key": "TEST-PCHILD2", "fields": {"summary": "Parent Child 2", "status": {"name": "In Progress"}}}
        ]
        self.mock_client.get_parent_link_children.return_value = ["TEST-PCHILD1", "TEST-PCHILD2"]
        
        result = asyncio.run(self.tools.get_children(
            "TEST-PARENT", 
            include_parent_links=True,
            parent_link_field="Custom Parent"
        ))
        
        self.mock_client.get_parent_link_children.assert_called_once_with("TEST-PARENT", "Custom Parent")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].key, "TEST-PCHILD1")
        self.assertEqual(result[1].key, "TEST-PCHILD2")

    def test_tools_20_get_children_handles_parent_link_errors(self):
        """TOOLS-20: Get children handles parent link fetch errors gracefully."""
        self.mock_client.get_issue.side_effect = [
            {"key": "TEST-PARENT", "fields": {"subtasks": []}},
            Exception("Network error")  # Second call fails
        ]
        self.mock_client.get_parent_link_children.return_value = ["TEST-FAIL"]
        
        result = asyncio.run(self.tools.get_children("TEST-PARENT", include_parent_links=True))
        
        # Should return empty list since subtasks were empty and parent-link child failed
        self.assertEqual(len(result), 0)

    def test_tools_21_get_linked_issues_all_links(self):
        """TOOLS-21: Get linked issues returns all links."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-CENTRAL",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "Blocks", "inward": "is blocked by", "outward": "blocks"},
                        "inwardIssue": {"key": "TEST-BLOCKER"}
                    },
                    {
                        "type": {"name": "Relates", "inward": "relates to", "outward": "relates to"},
                        "outwardIssue": {"key": "TEST-RELATED"}
                    },
                    {
                        "type": {"name": "Duplicates", "inward": "is duplicated by", "outward": "duplicates"},
                        "outwardIssue": {"key": "TEST-DUP"}
                    }
                ]
            }
        }
        
        result = asyncio.run(self.tools.get_linked_issues("TEST-CENTRAL"))
        
        self.assertEqual(len(result), 3)
        link_keys = [link.issue_key for link in result]
        self.assertIn("TEST-BLOCKER", link_keys)
        self.assertIn("TEST-RELATED", link_keys)
        self.assertIn("TEST-DUP", link_keys)

    def test_tools_22_get_linked_issues_with_filter(self):
        """TOOLS-22: Get linked issues with link type filter."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-FILTER",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "Blocks", "inward": "is blocked by", "outward": "blocks"},
                        "inwardIssue": {"key": "TEST-BLOCKER"}
                    },
                    {
                        "type": {"name": "Relates", "inward": "relates to", "outward": "relates to"},
                        "outwardIssue": {"key": "TEST-RELATED"}
                    }
                ]
            }
        }
        
        result = asyncio.run(self.tools.get_linked_issues("TEST-FILTER", link_type="Blocks"))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].issue_key, "TEST-BLOCKER")
        self.assertEqual(result[0].link_type, "Blocks")

    def test_tools_23_get_linked_issues_case_insensitive_filter(self):
        """TOOLS-23: Get linked issues with case-insensitive filter."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-CASE",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "Blocks", "inward": "is blocked by", "outward": "blocks"},
                        "inwardIssue": {"key": "TEST-MATCH"}
                    }
                ]
            }
        }
        
        result = asyncio.run(self.tools.get_linked_issues("TEST-CASE", link_type="blocks"))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].issue_key, "TEST-MATCH")

    def test_tools_24_get_linked_issues_no_matches(self):
        """TOOLS-24: Get linked issues with no matching links."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-NOMATCH",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "Blocks", "inward": "is blocked by", "outward": "blocks"},
                        "inwardIssue": {"key": "TEST-OTHER"}
                    }
                ]
            }
        }
        
        result = asyncio.run(self.tools.get_linked_issues("TEST-NOMATCH", link_type="NonExistent"))
        
        self.assertEqual(len(result), 0)

    def test_tools_25_get_linked_issues_handles_missing_link_data(self):
        """TOOLS-25: Get linked issues handles missing or malformed link data."""
        self.mock_client.get_issue.return_value = {
            "key": "TEST-MALFORMED",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "Blocks"},  # Missing inward/outward
                        "inwardIssue": {"key": "TEST-VALID"}
                    },
                    {
                        "type": {},  # Missing name
                        "outwardIssue": {"key": "TEST-NONAME"}
                    },
                    {}  # Completely empty link
                ]
            }
        }
        
        result = asyncio.run(self.tools.get_linked_issues("TEST-MALFORMED"))
        
        # Should handle malformed data gracefully
        self.assertEqual(len(result), 2)  # Only the valid ones
        self.assertEqual(result[0].link_type, "Blocks")
        self.assertEqual(result[1].link_type, "unknown")  # Fallback for missing name

    def test_tools_26_get_parent_with_subtask_parent(self):
        """TOOLS-26: Get parent with subtask parent relationship."""
        self.mock_client.get_issue.return_value = {
            "fields": {
                "parent": {
                    "key": "TEST-PARENT",
                    "fields": {
                        "summary": "Parent Issue Summary"
                    }
                }
            }
        }
        
        result = asyncio.run(self.tools.get_parent("TEST-CHILD"))
        
        self.assertIsInstance(result, ParentInfo)
        self.assertEqual(result.issue_key, "TEST-CHILD")
        self.assertEqual(result.parent_key, "TEST-PARENT")
        self.assertEqual(result.parent_summary, "Parent Issue Summary")
        self.assertEqual(result.parent_type, "subtask")

    def test_tools_27_get_parent_with_no_parent(self):
        """TOOLS-27: Get parent with no parent relationship."""
        self.mock_client.get_issue.return_value = {"fields": {}}
        self.mock_client.get_field_by_name.return_value = None
        
        result = asyncio.run(self.tools.get_parent("TEST-ORPHAN"))
        
        self.assertIsInstance(result, ParentInfo)
        self.assertEqual(result.issue_key, "TEST-ORPHAN")
        self.assertIsNone(result.parent_key)
        self.assertIsNone(result.parent_summary)
        self.assertIsNone(result.parent_type)

    def test_tools_28_get_parent_with_parent_link_field(self):
        """TOOLS-28: Get parent with custom parent link field."""
        self.mock_client.get_issue.return_value = {"fields": {}}  # Child issue with no subtask parent and no parent link value
        self.mock_client.get_field_by_name.return_value = {"id": "customfield_12345"}
        
        result = asyncio.run(self.tools.get_parent("TEST-CHILD", parent_link_field="Epic Link"))
        
        # Should call get_issue once: only for the child (no parent link value means no second call)
        self.assertEqual(self.mock_client.get_issue.call_count, 1)
        
        self.assertEqual(result.issue_key, "TEST-CHILD")
        self.assertIsNone(result.parent_key)  # No parent link value in fields

    def test_tools_29_get_parent_with_parent_link_value(self):
        """TOOLS-29: Get parent with parent link field containing value."""
        self.mock_client.get_issue.side_effect = [
            {"fields": {"customfield_12345": "TEST-EPIC"}},  # Child with parent link
            {"fields": {"summary": "Epic Summary"}}  # Parent issue
        ]
        self.mock_client.get_field_by_name.return_value = {"id": "customfield_12345"}
        
        result = asyncio.run(self.tools.get_parent("TEST-CHILD", parent_link_field="Epic Link"))
        
        self.assertEqual(result.issue_key, "TEST-CHILD")
        self.assertEqual(result.parent_key, "TEST-EPIC")
        self.assertEqual(result.parent_summary, "Epic Summary")
        self.assertEqual(result.parent_type, "parent_link(Epic Link)")

    def test_tools_30_get_ancestors_single_level(self):
        """TOOLS-30: Get ancestors with single level hierarchy."""
        # Mock get_parent calls
        async def mock_get_parent(issue_key, include_parent_links=True, parent_link_field="Parent Link"):
            if issue_key == "TEST-CHILD":
                return ParentInfo(
                    issue_key="TEST-CHILD",
                    parent_key="TEST-PARENT", 
                    parent_summary="Parent Summary",
                    parent_type="subtask"
                )
            else:
                return ParentInfo(
                    issue_key="TEST-PARENT",
                    parent_key=None,
                    parent_summary=None,
                    parent_type=None
                )
        
        self.tools.get_parent = mock_get_parent
        self.mock_client.get_issue.return_value = {
            "fields": {
                "summary": "Parent Summary",
                "status": {"name": "Open"}
            }
        }
        
        result = asyncio.run(self.tools.get_ancestors("TEST-CHILD"))
        
        self.assertIsInstance(result, AncestorTree)
        self.assertEqual(result.root_issue, "TEST-CHILD")
        self.assertEqual(result.total_ancestors, 1)
        self.assertEqual(len(result.ancestors), 1)
        self.assertEqual(result.ancestors[0].key, "TEST-PARENT")
        self.assertEqual(len(result.traversal_order), 1)

    def test_tools_31_get_ancestors_multi_level(self):
        """TOOLS-31: Get ancestors with multi-level hierarchy."""
        # Mock get_parent calls for 3-level hierarchy
        async def mock_get_parent(issue_key, include_parent_links=True, parent_link_field="Parent Link"):
            parent_map = {
                "TEST-CHILD": ParentInfo(issue_key="TEST-CHILD", parent_key="TEST-PARENT", parent_summary="Parent Summary", parent_type="subtask"),
                "TEST-PARENT": ParentInfo(issue_key="TEST-PARENT", parent_key="TEST-GRANDPARENT", parent_summary="Grandparent Summary", parent_type="subtask"),
                "TEST-GRANDPARENT": ParentInfo(issue_key="TEST-GRANDPARENT", parent_key=None, parent_summary=None, parent_type=None)
            }
            return parent_map.get(issue_key, ParentInfo(issue_key=issue_key, parent_key=None, parent_summary=None, parent_type=None))
        
        self.tools.get_parent = mock_get_parent
        self.mock_client.get_issue.side_effect = [
            {"fields": {"summary": "Parent Summary", "status": {"name": "Open"}}},
            {"fields": {"summary": "Grandparent Summary", "status": {"name": "In Progress"}}}
        ]
        
        result = asyncio.run(self.tools.get_ancestors("TEST-CHILD"))
        
        self.assertEqual(result.total_ancestors, 2)
        self.assertEqual(len(result.ancestors), 2)
        self.assertEqual(result.ancestors[0].key, "TEST-PARENT")
        self.assertEqual(result.ancestors[1].key, "TEST-GRANDPARENT")
        self.assertEqual(len(result.traversal_order), 2)

    def test_tools_32_get_ancestors_with_depth_limit(self):
        """TOOLS-32: Get ancestors with depth limit."""
        # Mock get_parent calls for 3-level hierarchy
        async def mock_get_parent(issue_key, include_parent_links=True, parent_link_field="Parent Link"):
            parent_map = {
                "TEST-CHILD": ParentInfo(issue_key="TEST-CHILD", parent_key="TEST-PARENT", parent_summary="Parent Summary", parent_type="subtask"),
                "TEST-PARENT": ParentInfo(issue_key="TEST-PARENT", parent_key="TEST-GRANDPARENT", parent_summary="Grandparent Summary", parent_type="subtask"),
                "TEST-GRANDPARENT": ParentInfo(issue_key="TEST-GRANDPARENT", parent_key=None, parent_summary=None, parent_type=None)
            }
            return parent_map.get(issue_key, ParentInfo(issue_key=issue_key, parent_key=None, parent_summary=None, parent_type=None))
        
        self.tools.get_parent = mock_get_parent
        self.mock_client.get_issue.return_value = {
            "fields": {"summary": "Parent Summary", "status": {"name": "Open"}}
        }
        
        # Limit to depth 1
        result = asyncio.run(self.tools.get_ancestors("TEST-CHILD", max_depth=1))
        
        self.assertEqual(result.max_depth, 1)
        self.assertEqual(result.total_ancestors, 1)
        self.assertEqual(result.ancestors[0].key, "TEST-PARENT")

    def test_tools_33_get_ancestors_no_ancestors(self):
        """TOOLS-33: Get ancestors for issue with no parents."""
        async def mock_get_parent(issue_key, include_parent_links=True, parent_link_field="Parent Link"):
            return ParentInfo(issue_key=issue_key, parent_key=None, parent_summary=None, parent_type=None)
        
        self.tools.get_parent = mock_get_parent
        
        result = asyncio.run(self.tools.get_ancestors("TEST-ORPHAN"))
        
        self.assertEqual(result.total_ancestors, 0)
        self.assertEqual(len(result.ancestors), 0)
        self.assertEqual(len(result.traversal_order), 0)

    def test_tools_34_get_ancestors_handles_fetch_errors(self):
        """TOOLS-34: Get ancestors handles parent fetch errors gracefully."""
        async def mock_get_parent(issue_key, include_parent_links=True, parent_link_field="Parent Link"):
            if issue_key == "TEST-CHILD":
                return ParentInfo(issue_key="TEST-CHILD", parent_key="TEST-PARENT", parent_summary="Parent Summary", parent_type="subtask")
            else:
                return ParentInfo(issue_key="TEST-PARENT", parent_key=None, parent_summary=None, parent_type=None)
        
        self.tools.get_parent = mock_get_parent
        # Make get_issue raise an exception
        self.mock_client.get_issue.side_effect = Exception("JIRA API error")
        
        result = asyncio.run(self.tools.get_ancestors("TEST-CHILD"))
        
        # Should stop traversal on error but not crash
        self.assertEqual(result.total_ancestors, 0)
        self.assertEqual(len(result.ancestors), 0)

    def test_tools_35_get_ancestors_prevents_cycles(self):
        """TOOLS-35: Get ancestors prevents infinite loops from cycles."""
        # Create a cycle: CHILD -> PARENT -> CHILD
        async def mock_get_parent(issue_key, include_parent_links=True, parent_link_field="Parent Link"):
            cycle_map = {
                "TEST-CHILD": ParentInfo(issue_key="TEST-CHILD", parent_key="TEST-PARENT", parent_summary="Parent Summary", parent_type="subtask"),
                "TEST-PARENT": ParentInfo(issue_key="TEST-PARENT", parent_key="TEST-CHILD", parent_summary="Child Summary", parent_type="subtask")
            }
            return cycle_map.get(issue_key, ParentInfo(issue_key=issue_key, parent_key=None, parent_summary=None, parent_type=None))
        
        self.tools.get_parent = mock_get_parent
        self.mock_client.get_issue.return_value = {
            "fields": {"summary": "Parent Summary", "status": {"name": "Open"}}
        }
        
        result = asyncio.run(self.tools.get_ancestors("TEST-CHILD"))
        
        # Should only traverse once and stop when hitting visited issue
        self.assertEqual(result.total_ancestors, 1)
        self.assertEqual(result.ancestors[0].key, "TEST-PARENT")

    def test_tools_36_dynamic_field_discovery_via_editmeta_api(self):
        """TOOLS-36: Dynamic field discovery via editmeta API."""
        # Mock editmeta response with Epic Link field
        editmeta_response = {
            "fields": {
                "customfield_12311140": {
                    "name": "Epic Link",
                    "schema": {"custom": "com.pyxis.greenhopper.jira:gh-epic-link"}
                },
                "customfield_12345": {
                    "name": "Some Other Field", 
                    "schema": {"custom": "com.example:other"}
                }
            }
        }
        
        self.mock_client._make_api_request.return_value = editmeta_response
        
        # Test field discovery
        parent_fields = self.tools._get_parent_fields_for_issue("TEST-123", "TEST", "Story")
        
        # Should find the Epic Link field
        self.assertEqual(parent_fields, ["customfield_12311140"])
        
        # Verify API was called correctly  
        expected_url = "https://test.jira.com/rest/api/issue/TEST-123/editmeta"
        self.mock_client._make_api_request.assert_called_with(expected_url, resource_name="editmeta")

    def test_tools_37_ttl_cache_stores_and_retrieves_field_mappings(self):
        """TOOLS-37: TTL cache stores and retrieves field mappings."""
        # Mock editmeta response
        editmeta_response = {
            "fields": {
                "customfield_12311140": {
                    "name": "Epic Link",
                    "schema": {"custom": "com.pyxis.greenhopper.jira:gh-epic-link"}
                }
            }
        }
        self.mock_client._make_api_request.return_value = editmeta_response
        
        # First call should hit the API
        result1 = self.tools._get_parent_fields_for_issue("TEST-123", "TEST", "Story")
        self.assertEqual(result1, ["customfield_12311140"])
        self.assertEqual(self.mock_client._make_api_request.call_count, 1)
        
        # Second call should use cache
        result2 = self.tools._get_parent_fields_for_issue("TEST-123", "TEST", "Story")
        self.assertEqual(result2, ["customfield_12311140"])
        # Should still be 1 call (cached)
        self.assertEqual(self.mock_client._make_api_request.call_count, 1)

    def test_tools_38_ttl_cache_expires_entries_after_configured_timeout(self):
        """TOOLS-38: TTL cache expires entries after configured timeout."""
        import time
        
        # Create tools with very short TTL (0.1 seconds)
        short_ttl_tools = JiraTools(self.mock_client, field_cache_ttl=0.1)
        
        editmeta_response = {
            "fields": {
                "customfield_12311140": {
                    "name": "Epic Link", 
                    "schema": {"custom": "com.pyxis.greenhopper.jira:gh-epic-link"}
                }
            }
        }
        self.mock_client._make_api_request.return_value = editmeta_response
        
        # First call
        result1 = short_ttl_tools._get_parent_fields_for_issue("TEST-123", "TEST", "Story")
        self.assertEqual(result1, ["customfield_12311140"])
        self.assertEqual(self.mock_client._make_api_request.call_count, 1)
        
        # Wait for cache to expire
        time.sleep(0.2)
        
        # Cache should be expired, API called again
        result2 = short_ttl_tools._get_parent_fields_for_issue("TEST-123", "TEST", "Story")
        self.assertEqual(result2, ["customfield_12311140"])
        self.assertEqual(self.mock_client._make_api_request.call_count, 2)

    def test_tools_39_get_parent_uses_discovered_fields_before_fallback(self):
        """TOOLS-39: Get parent uses discovered fields before fallback."""
        # Mock issue with project and issuetype
        issue_data = {
            "fields": {
                "project": {"key": "TEST"},
                "issuetype": {"name": "Story"},
                "customfield_12311140": "TEST-PARENT"
            }
        }
        
        # Mock editmeta response
        editmeta_response = {
            "fields": {
                "customfield_12311140": {
                    "name": "Epic Link",
                    "schema": {"custom": "com.pyxis.greenhopper.jira:gh-epic-link"}
                }
            }
        }
        
        parent_data = {"fields": {"summary": "Parent Summary"}}
        
        self.mock_client.get_issue.side_effect = [issue_data, parent_data]
        self.mock_client._make_api_request.return_value = editmeta_response
        
        result = asyncio.run(self.tools.get_parent("TEST-CHILD"))
        
        # Should find parent using discovered field
        self.assertEqual(result.parent_key, "TEST-PARENT")
        self.assertEqual(result.parent_type, "parent_field(customfield_12311140)")
        
        # Should NOT call get_field_by_name (fallback)
        self.mock_client.get_field_by_name.assert_not_called()

    def test_tools_40_get_parent_fallback_when_editmeta_fails(self):
        """TOOLS-40: Get parent fallback when editmeta fails."""
        # Mock issue data
        issue_data = {
            "fields": {
                "project": {"key": "TEST"},
                "issuetype": {"name": "Story"},
                "customfield_12345": "TEST-PARENT"
            }
        }
        
        parent_data = {"fields": {"summary": "Parent Summary"}}
        
        # Make editmeta API fail
        self.mock_client._make_api_request.side_effect = Exception("API Error")
        self.mock_client.get_issue.side_effect = [issue_data, parent_data]
        self.mock_client.get_field_by_name.return_value = {"id": "customfield_12345"}
        
        result = asyncio.run(self.tools.get_parent("TEST-CHILD", parent_link_field="Epic Link"))
        
        # Should find parent using fallback method
        self.assertEqual(result.parent_key, "TEST-PARENT")
        self.assertEqual(result.parent_type, "parent_link(Epic Link)")
        
        # Should call fallback method
        self.mock_client.get_field_by_name.assert_called_with("Epic Link")

    def test_tools_41_get_parent_chooses_first_field_when_multiple_have_values(self):
        """TOOLS-41: Get parent chooses first field when multiple have values."""
        # Mock issue with BOTH parent fields having values
        issue_data = {
            "fields": {
                "project": {"key": "TEST"},
                "issuetype": {"name": "Epic"},
                "customfield_12311140": "TEST-EPIC",      # Epic Link has value
                "customfield_12313140": "TEST-PARENT"     # Parent Link ALSO has value
            }
        }
        
        # Mock editmeta response with both field types
        editmeta_response = {
            "fields": {
                "customfield_12311140": {
                    "name": "Epic Link",
                    "schema": {"custom": "com.pyxis.greenhopper.jira:gh-epic-link"}
                },
                "customfield_12313140": {
                    "name": "Parent Link",
                    "schema": {"custom": "com.atlassian.jpo:jpo-custom-field-parent"}
                }
            }
        }
        
        parent_data = {"fields": {"summary": "Epic Summary"}}
        
        self.mock_client.get_issue.side_effect = [issue_data, parent_data]
        self.mock_client._make_api_request.return_value = editmeta_response
        
        result = asyncio.run(self.tools.get_parent("TEST-CHILD"))
        
        # Should use Epic Link (first discovered) and ignore Parent Link
        self.assertEqual(result.parent_key, "TEST-EPIC")
        self.assertEqual(result.parent_type, "parent_field(customfield_12311140)")

    def test_tools_42_field_discovery_handles_missing_project_issue_type(self):
        """TOOLS-42: Field discovery handles missing project/issue type."""
        # Mock issue without project/issuetype fields
        issue_data = {
            "fields": {
                "customfield_12345": "TEST-PARENT"
            }
        }
        
        parent_data = {"fields": {"summary": "Parent Summary"}}
        
        self.mock_client.get_issue.side_effect = [issue_data, parent_data]
        self.mock_client.get_field_by_name.return_value = {"id": "customfield_12345"}
        
        result = asyncio.run(self.tools.get_parent("TEST-CHILD", parent_link_field="Epic Link"))
        
        # Should skip dynamic discovery and use fallback
        self.assertEqual(result.parent_key, "TEST-PARENT")
        self.assertEqual(result.parent_type, "parent_link(Epic Link)")
        
        # Should not call editmeta API
        self.mock_client._make_api_request.assert_not_called()

    def test_tools_43_field_discovery_identifies_epic_link_schema_type(self):
        """TOOLS-43: Field discovery identifies Epic Link schema type."""
        editmeta_response = {
            "fields": {
                "customfield_12311140": {
                    "name": "Epic Link",
                    "schema": {"custom": "com.pyxis.greenhopper.jira:gh-epic-link"}
                },
                "customfield_99999": {
                    "name": "Other Field",
                    "schema": {"custom": "com.example:other-type"}
                }
            }
        }
        
        self.mock_client._make_api_request.return_value = editmeta_response
        
        result = self.tools._get_parent_fields_for_issue("TEST-123", "TEST", "Story")
        
        # Should only find Epic Link field
        self.assertEqual(result, ["customfield_12311140"])

    def test_tools_44_field_discovery_identifies_parent_link_schema_type(self):
        """TOOLS-44: Field discovery identifies Parent Link schema type."""
        editmeta_response = {
            "fields": {
                "customfield_12313140": {
                    "name": "Parent Link",
                    "schema": {"custom": "com.atlassian.jpo:jpo-custom-field-parent"}
                },
                "customfield_99999": {
                    "name": "Other Field",
                    "schema": {"custom": "com.example:other-type"}
                }
            }
        }
        
        self.mock_client._make_api_request.return_value = editmeta_response
        
        result = self.tools._get_parent_fields_for_issue("TEST-123", "TEST", "Epic")
        
        # Should only find Parent Link field
        self.assertEqual(result, ["customfield_12313140"])

    def test_tools_45_get_ancestors_with_dynamic_field_discovery(self):
        """TOOLS-45: Get ancestors with dynamic field discovery."""
        # Mock get_parent calls directly since ancestors just calls get_parent repeatedly
        async def mock_get_parent(issue_key, include_parent_links=True, parent_link_field="Parent Link"):
            if issue_key == "TEST-CHILD":
                return ParentInfo(
                    issue_key="TEST-CHILD",
                    parent_key="TEST-PARENT",
                    parent_summary="Parent Summary",
                    parent_type="parent_field(customfield_12311140)"
                )
            elif issue_key == "TEST-PARENT":
                return ParentInfo(
                    issue_key="TEST-PARENT", 
                    parent_key=None,
                    parent_summary=None,
                    parent_type=None
                )
            return ParentInfo(issue_key=issue_key, parent_key=None, parent_summary=None, parent_type=None)
        
        # Mock the get_issue calls that ancestors uses for creating IssueSummary objects
        def mock_get_issue(issue_key, expand=None):
            if issue_key == "TEST-PARENT":
                return {
                    "key": "TEST-PARENT",
                    "fields": {
                        "summary": "Parent Summary",
                        "status": {"name": "Open"}
                    }
                }
            return {
                "key": issue_key,
                "fields": {"summary": "Default Summary", "status": {"name": "Open"}}
            }
        
        self.mock_client.get_issue.side_effect = mock_get_issue
        
        # Patch get_parent to use our mock
        with patch.object(self.tools, 'get_parent', side_effect=mock_get_parent):
            result = asyncio.run(self.tools.get_ancestors("TEST-CHILD"))
        
        # Should find ancestors using dynamic discovery
        self.assertEqual(result.total_ancestors, 1)
        self.assertEqual(result.ancestors[0].key, "TEST-PARENT")


if __name__ == "__main__":
    unittest.main(verbosity=2) 
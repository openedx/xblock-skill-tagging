"""
Tests for SkillTaggingMixin
"""
from __future__ import absolute_import

import unittest
from unittest.mock import Mock, patch

from test_utils import TestCaseMixin, get_tagging_mixin


@patch('skill_tagging.skill_tagging_mixin.get_api_client')
class SkillTaggingMixinTests(TestCaseMixin, unittest.TestCase):
    """
    Test suite for SkillTaggingMixin
    """

    def test_mixin_fields(self, _):
        """
        Test for mixin field and methods
        """
        self.tagging_mixin = get_tagging_mixin()
        self.assertTrue(hasattr(self.tagging_mixin, 'has_verified_tags'))
        self.assertTrue(hasattr(self.tagging_mixin, 'fetch_skill_tags'))
        self.assertTrue(hasattr(self.tagging_mixin, 'verify_tags'))

    def test_fetch_tags(self, mock_get_api_client):
        """
        Test that fetch_tags method works as expected
        """
        api_client = self.get_mock_api_response()
        mock_get_api_client.return_value = api_client
        resp = self.block.fetch_skill_tags()
        assert mock_get_api_client.call_count == 1
        assert api_client.get.call_count == 1
        expected_response = [
            {'id': 1, 'name': 'SKILL-0'},
            {'id': 6, 'name': 'SKILL-5'}
        ]
        self.assertEqual(resp, expected_response)

    @patch('skill_tagging.skill_tagging_mixin.XBLOCK_SKILL_VERIFIED')
    def test_verify_tags(self, mock_event, _):
        """
        Test that verify_tags method works as expected
        """
        mock_event.return_value = Mock(send_event=Mock())
        selected_tags = [1, 6]
        ignored_tags = []
        self.assertFalse(self.block.has_verified_tags)
        self.call_handler(self.VERIFY_TAGS_HANDLER, data={
            "verified_skills": selected_tags,
            "ignored_skills": ignored_tags,
        })
        assert mock_event.send_event.call_count == 1
        self.assertTrue(self.block.has_verified_tags)

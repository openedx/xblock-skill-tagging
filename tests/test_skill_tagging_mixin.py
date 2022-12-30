"""
Tests for SkillTaggingMixin
"""
from __future__ import absolute_import

import json
import unittest
from unittest.mock import Mock, patch

from requests.models import Response
from rest_framework import status

from .utils import TestCaseMixin, get_tagging_mixin, make_block


@patch('skill_tagging.skill_tagging_mixin.get_api_client')
class SkillTaggingMixinTests(unittest.TestCase, TestCaseMixin):
    """
    Test suite for SkillTaggingMixin
    """

    def setUp(self):
        self.block = make_block()
        self.patch_workbench()
        fake_user = Mock()
        fake_user.opt_attrs = {
            'edx-platform.user_role': 'student',
            'edx-platform.is_authenticated': True,
        }
        mock_user_service = Mock()
        mock_user_service.get_current_user.return_value = fake_user
        self.block.runtime.service = Mock(return_value=mock_user_service)

    def _mock_response(self, status_code, content=None):
        """
        Generates a python core response.
        """
        mock_response = Response()
        mock_response.status_code = status_code
        # pylint: disable=protected-access
        mock_response._content = json.dumps(content).encode('utf-8')
        return mock_response

    # pylint: disable=unused-argument
    def test_mixin_fields(self, mock_get_api_client):
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
        sample_output = {
            "results": [{
                "id": 1,
                "skills": [
                    {
                        "id": 1,
                        "name": "SKILL-0"
                    },
                    {
                        "id": 6,
                        "name": "SKILL-5"
                    },
                ],
            }]
        }
        api_client = Mock(
            get=Mock(
                return_value=self._mock_response(
                    status.HTTP_200_OK,
                    sample_output
                )
            )
        )
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

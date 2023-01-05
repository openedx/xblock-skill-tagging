"""
Tests for pipeline.py
"""
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from openedx_filters.learning.filters import VerticalBlockRenderCompleted

from test_utils import TestCaseMixin


@patch('skill_tagging.skill_tagging_mixin.get_api_client')
@override_settings(
    OPEN_EDX_FILTERS_CONFIG={
        "org.openedx.learning.vertical_block.render.completed.v1": {
            "fail_silently": False,
            "pipeline": [
                "skill_tagging.pipeline.AddVerticalBlockSkillVerificationSection"
            ]
        }
    },
    SHOW_SKILL_VERIFICATION_PROBABILITY=0,
)
class TestAddVerticalBlockSkillVerificationSection(TestCaseMixin, TestCase):
    """
    Testcase for the AddVerticalBlockSkillVerificationSection openedx-filters pipeline.
    """

    def setUp(self) -> None:
        super().setUp()
        self.original_fragement = Mock(content="<p>Some</p>")

    @override_settings(
        SHOW_SKILL_VERIFICATION_PROBABILITY=0,
    )
    def test_pipeline_does_nothing_when_probability_set_to_zero(self, mock_get_api_client):
        """
        Check that the input fragment is unchanged when there is no
        configuration for a course.
        """
        mock_get_api_client.return_value = self.get_mock_api_response()
        _, fragment, _, _ = VerticalBlockRenderCompleted.run_filter(
            block=self.block, context={}, fragment=self.original_fragement, view={}
        )
        self.assertEqual(fragment.content, self.original_fragement.content)
        self.assertNotIn("SKILL-0", fragment.content)

    @override_settings(
        SHOW_SKILL_VERIFICATION_PROBABILITY=1,
    )
    def test_pipeline_adds_edit_link_when_probability_set_to_one(self, mock_get_api_client):
        """Check that verification div is added with skills."""
        mock_get_api_client.return_value = self.get_mock_api_response()
        _, fragment, _, _ = VerticalBlockRenderCompleted.run_filter(
            block=self.block, context={}, fragment=self.original_fragement, view={}
        )

        self.assertIn(self.original_fragement.content, fragment.content)
        self.assertIn("SKILL-0", fragment.content)
        self.assertIn("SKILL-5", fragment.content)

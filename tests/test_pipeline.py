"""
Tests for pipeline.py
"""
from unittest.mock import patch

from django.test import TestCase, override_settings
from openedx_filters.learning.filters import VerticalBlockChildRenderStarted, VerticalBlockRenderCompleted
from workbench.runtime import Fragment

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
        self.original_fragement = Fragment(content="Some")

    @override_settings(
        SHOW_SKILL_VERIFICATION_PROBABILITY=0,
    )
    def test_pipeline_does_nothing_when_probability_set_to_zero(self, mock_get_api_client):
        """Check that pipeline is not executed if probability is set to zero"""
        mock_get_api_client.return_value = self.get_mock_api_response()
        _, fragment, _, _ = VerticalBlockRenderCompleted.run_filter(
            block=self.block, context={}, fragment=self.original_fragement, view={}
        )
        mock_get_api_client.assert_not_called()
        self.assertEqual(fragment.content, self.original_fragement.content)
        self.assertNotIn("SKILL-0", fragment.content)

    @override_settings(
        SHOW_SKILL_VERIFICATION_PROBABILITY=1,
    )
    def test_pipeline_adds_verification_form_when_probability_set_to_one(self, mock_get_api_client):
        """Check that verification div is added with skills."""
        mock_get_api_client.return_value = self.get_mock_api_response()
        _, fragment, _, _ = VerticalBlockRenderCompleted.run_filter(
            block=self.block, context={}, fragment=self.original_fragement, view={}
        )

        self.assertIn(self.original_fragement.content, fragment.content)
        self.assertIn("SKILL-0", fragment.content)
        self.assertIn("SKILL-5", fragment.content)


@patch('skill_tagging.skill_tagging_mixin.get_api_client')
@override_settings(
    OPEN_EDX_FILTERS_CONFIG={
        "org.openedx.learning.vertical_block_child.render.started.v1": {
            "fail_silently": False,
            "pipeline": [
                "skill_tagging.pipeline.AddVideoBlockSkillVerificationComponent"
            ]
        }
    },
    SHOW_SKILL_VERIFICATION_PROBABILITY=1,
)
class TestAddVideoBlockSkillVerificationComponent(TestCaseMixin, TestCase):
    """
    Testcase for the AddVerticalBlockSkillVerificationSection openedx-filters pipeline.
    """

    def setUp(self) -> None:
        self.block_type = "video"
        super().setUp()
        self.original_fragement = Fragment(content="<div class='video-player'></div>")
        self.block.fragment = self.original_fragement

    @override_settings(
        SHOW_SKILL_VERIFICATION_PROBABILITY=0,
    )
    def test_pipeline_does_nothing_when_probability_set_to_zero(self, mock_get_api_client):
        """Check that pipeline is not executed if probability is set to zero"""
        mock_get_api_client.return_value = self.get_mock_api_response()
        _, fragment, _, _ = VerticalBlockRenderCompleted.run_filter(
            block=self.block, context={}, fragment=self.original_fragement, view={}
        )
        mock_get_api_client.assert_not_called()
        self.assertEqual(fragment.content, self.original_fragement.content)
        self.assertNotIn("SKILL-0", fragment.content)

    def test_pipeline_adds_required_resources(self, mock_get_api_client):
        """Check that pipeline adds required resources."""
        mock_get_api_client.return_value = self.get_mock_api_response()
        block, context = VerticalBlockChildRenderStarted.run_filter(block=self.block, context={})
        fragment = block.student_view(context)

        self.assertEqual(fragment.content, self.original_fragement.content)
        self.assertEqual(len(fragment.resources), 3)
        for resource in fragment.resources:
            self.assertIn(resource.mimetype, ("text/css", "application/javascript"))

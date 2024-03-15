"""
Module that contains the openedx_filters pipeline steps.
"""
import logging
import random

import pkg_resources
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep

try:
    from edx_proctoring.models import ProctoredExam
except ImportError:
    ProctoredExam = None

logger = logging.getLogger(__name__)
DEFAULT_PROBABILITY = 0.03


def resource_string(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


class VerificationPipelineBase:
    """
    Common functions for verification pipelines.
    """
    @staticmethod
    def fetch_related_skills(block):
        """Checks `has_verified_tags` and fetchs related skills."""
        has_verified_tags = getattr(block, "has_verified_tags", None)
        if has_verified_tags is None or has_verified_tags is True:
            return []
        fetch_tags = getattr(block, "fetch_skill_tags", None)
        if fetch_tags is None:
            return []
        tags = fetch_tags()
        return tags

    @staticmethod
    def is_proctored_exam(content_id):
        """Determines whether the content is a proctored exam."""
        if ProctoredExam:
            return ProctoredExam.objects.filter(content_id=content_id, is_proctored=True).exists()
        return False

    @staticmethod
    def should_run_filter():
        """Determines whether we should run filter and display form."""
        # random returns a number between 0 and 1 (inclusive).
        probability = getattr(settings, "SHOW_SKILL_VERIFICATION_PROBABILITY", DEFAULT_PROBABILITY)
        return random.random() < probability

    @staticmethod
    def get_skill_context(usage_id, block, skills):
        """
        Build common skill context data used by templates.
        """
        verify_tags_url = block.runtime.handler_url(block, "verify_tags")
        data = {
            "block_type": usage_id.block_type,
            "block_id": usage_id.block_id,
            "verify_tags_url": verify_tags_url,
            "skills": skills,
            "tag_verification_template": Template(resource_string("static/tagging.html")),
            "form": Template(resource_string("static/tags_form.html")),
            "thank_you_section": Template(resource_string("static/tags_thankyou.html")),
            "error_section": Template(resource_string("static/tags_error.html")),
            "image": resource_string("static/brainstorming.svg"),
        }
        return data


class AddVerticalBlockSkillVerificationSection(VerificationPipelineBase, PipelineStep):
    """
    Adds extra HTML to the fragment.

    Example Usage:

    .. code-block::

        "OPENEDX_FILTERS_CONFIG": {
            "org.openedx.learning.vertical_block.render.completed.v1": {
                "fail_sliently": false,
                "pipeline": [
                    "skill_tagging.pipeline.AddVerticalBlockSkillVerificationSection"
                ]
            }
        }
    """
    def run_filter(self, block, fragment, context, view):  # pylint: disable=arguments-differ
        """Pipeline Step implementing the Filter"""
        usage_id = block.scope_ids.usage_id
        # Check whether we need to run this filter and only call the API.
        if not self.should_run_filter() or self.is_proctored_exam(str(usage_id)):
            return {"block": block, "fragment": fragment, "context": context, "view": view}
        skills = self.fetch_related_skills(block)
        if not skills:
            return {"block": block, "fragment": fragment, "context": context, "view": view}
        data = self.get_skill_context(usage_id, block, skills)
        html = resource_string("static/tagging.html")
        css = resource_string("static/tagging.css")
        js = resource_string("static/tagging.js")
        fragment.add_content(Template(html).render(Context(data)))
        fragment.add_javascript(js)
        fragment.add_css(css)
        return {"block": block, "fragment": fragment, "context": context, "view": view}


class AddVideoBlockSkillVerificationComponent(VerificationPipelineBase, PipelineStep):
    """
    Adds verification component to video blocks.

    Example Usage:

    .. code-block::

        "OPENEDX_FILTERS_CONFIG": {
            "org.openedx.learning.vertical_block_child.render.started.v1": {
                "fail_sliently": false,
                "pipeline": [
                    "skill_tagging.pipeline.AddVideoBlockSkillVerificationComponent"
                ]
            }
        }
    """
    def run_filter(self, block, context):  # pylint: disable=arguments-differ
        """Pipeline Step implementing the Filter"""
        usage_id = block.scope_ids.usage_id
        if usage_id.block_type != "video" or not self.should_run_filter():
            # avoid fetching skills for other xblocks
            return {"block": block, "context": context}
        skills = self.fetch_related_skills(block)
        if not skills:
            return {"block": block, "context": context}
        data = self.get_skill_context(usage_id, block, skills)

        def wrapper(fn):
            def wrapped(_context):
                fragment = fn(_context)
                js = resource_string("static/tagging.js")
                css = resource_string("static/tagging.css")
                fragment.add_javascript(Template(resource_string("static/video_tagging.js")).render(Context(data)))
                fragment.add_javascript(js)
                fragment.add_css(css)
                return fragment
            return wrapped
        block.student_view = wrapper(block.student_view)
        return {"block": block, "context": context}

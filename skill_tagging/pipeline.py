"""
Module that contains the openedx_filters pipeline steps.
"""
import logging
import pkg_resources

from django.template import Context, Template
from openedx_filters import PipelineStep

logger = logging.getLogger(__name__)


class AddVerticalBlockSkillVerificationSection(PipelineStep):
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
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def run_filter(self, block, fragment, context, view):
        """Pipeline Step implementing the Filter"""

        fetch_url = block.runtime.handler_url(block, "fetch_tags")
        verify_tags_url = block.runtime.handler_url(block, "verify_tags")
        html = self.resource_string("static/tagging.html")
        data = {"fetch_tags_url": fetch_url, "verify_tags_url": verify_tags_url}
        template = Template(html)
        context = Context(data)
        tags_div = template.render(context)
        fragment.content = f"{fragment.content}{tags_div}"
        return {"block": block, "fragment": fragment, "context": context, "view": view}

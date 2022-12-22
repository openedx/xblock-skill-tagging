"""
A mixin that fetches and verifies skills related to an Xblock,
that can be added for all XBlocks.
"""

import logging
from urllib.parse import urljoin

from django.conf import settings
from django.utils.translation import gettext as _
from openedx_events.learning.data import XBlockSkillVerificationData
from openedx_events.learning.signals import XBLOCK_SKILL_VERIFIED
from xblock.core import XBlock
from xblock.fields import Boolean, Scope

from .utils import get_api_client

LOGGER = logging.getLogger(__name__)
PAGE_SIZE = getattr(settings, "TAXONOMY_API_SKILL_PAGE_SIZE", 100)


# Make '_' a no-op so we can scrape strings
def _(text):
    return text


class SkillTaggingMixin:
    """
    XBlock Mixin for fetching and verifying skill tags
    """
    has_verified_tags = Boolean(
        display_name=_("Has verified tags"),
        default=False,
        help=_("Has user verified tags for this XBlock?"),
        scope=Scope.user_state
    )

    def _fetch_skill_tags(self):
        """
        Fetch skill tags for the XBlock by calling taxonomy api.
        """
        if not hasattr(settings, 'TAXONOMY_API_BASE_URL'):
            LOGGER.warning(
                "Require TAXONOMY_API_BASE_URL to be present in the settings."
            )
            return []

        user_service = self.runtime.service(self, 'user')
        if not user_service:
            LOGGER.info(
                "No user service available for this xblock. Cannot proceed."
            )
            return []

        user = user_service.get_user_by_anonymous_id()
        api_client = get_api_client(user=user)

        usage_id_str = str(self.scope_ids.usage_id)
        XBLOCK_SKILL_TAGS_API = urljoin(
            settings.TAXONOMY_API_BASE_URL,
            '/taxonomy/api/v1/xblocks'
        )
        response = api_client.get(
            XBLOCK_SKILL_TAGS_API,
            params={
                "usage_key": usage_id_str,
                "page_size": PAGE_SIZE,
                "verified": False,
            },
        )
        response.raise_for_status()
        results = response.json().get("results")
        if not results:
            LOGGER.info(
                f"XBlock<{usage_id_str}> does not contain any skill",
            )
            return []
        else:
            return results[0].get('skills', [])

    @XBlock.json_handler
    def fetch_tags(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Handler for fetching skill tags associated with this XBlock
        """
        return self._fetch_skill_tags()

    @XBlock.json_handler
    def verify_tags(self, tags, suffix=''):  # pylint: disable=unused-argument
        """
        Handler to verify tags
        """
        usage_key = str(self.scope_ids.usage_id)
        verified_skill_ids = []
        ignored_skill_ids = []
        if not self.has_verified_tags:
            skills = self._fetch_skill_tags()
            for skill in skills:
                if skill['name'] in tags:
                    verified_skill_ids.append(skill['id'])
                else:
                    ignored_skill_ids.append(skill['id'])
            XBLOCK_SKILL_VERIFIED.send_event(
                xblock_info=XBlockSkillVerificationData(
                    usage_key=usage_key,
                    verified_skills=verified_skill_ids,
                    ignored_skills=ignored_skill_ids,
                )
            )
            self.has_verified_tags = True

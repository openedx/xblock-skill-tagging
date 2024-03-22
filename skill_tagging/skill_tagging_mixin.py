"""
A mixin that fetches and verifies skills related to an Xblock,
that can be added for all XBlocks.
"""

import logging
from urllib.parse import urljoin

from django.conf import settings
from django.utils.timezone import datetime, timezone
from django.utils.translation import gettext as _
from openedx_events.learning.data import XBlockSkillVerificationData
from openedx_events.learning.signals import XBLOCK_SKILL_VERIFIED
from xblock.core import XBlock
from xblock.fields import Boolean, Scope
from xblock.internal import NamedAttributesMetaclass
from xblock.runtime import NoSuchServiceError

from .utils import get_api_client

LOGGER = logging.getLogger(__name__)
PAGE_SIZE = getattr(settings, "TAXONOMY_API_SKILL_PAGE_SIZE", 100)


# Make '_' a no-op so we can scrape strings
def _(text):
    return text


class SkillTaggingMixin(metaclass=NamedAttributesMetaclass):
    """
    XBlock Mixin for fetching and verifying skill tags
    """
    has_verified_tags = Boolean(
        display_name=_("Has verified tags"),
        default=False,
        help=_("Has user verified tags for this XBlock?"),
        scope=Scope.user_state
    )

    def _get_user_service(self):
        """
        Tries to get user service, if not found returns None.
        """
        try:
            user_service = self.runtime.service(self, 'user')
        except NoSuchServiceError:
            user_service = None
        return user_service

    def fetch_skill_tags(self):
        """
        Fetch skill tags for the XBlock by calling taxonomy api.
        """
        if not hasattr(settings, 'TAXONOMY_API_BASE_URL'):
            LOGGER.warning(
                "Require TAXONOMY_API_BASE_URL to be present in the settings."
            )
            return []

        user_service = self._get_user_service()
        if not user_service:
            LOGGER.info(
                "No user service available for this xblock. Cannot proceed."
            )
            return []

        user = user_service.get_user_by_anonymous_id()
        api_client = get_api_client(user=user)

        course_key_str = str(self.scope_ids.usage_id.context_key)
        usage_id_str = str(self.scope_ids.usage_id)
        XBLOCK_SKILL_TAGS_API = urljoin(
            settings.TAXONOMY_API_BASE_URL,
            '/taxonomy/api/v1/xblocks/'
        )
        response = api_client.get(
            XBLOCK_SKILL_TAGS_API,
            params={
                "course_key": course_key_str,
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
    def verify_tags(self, data, suffix=''):  # pylint: disable=unused-argument
        """
        Handler to verify tags
        """

        verified_skills = data.get("verified_skills", [])
        ignored_skills = data.get("ignored_skills", [])
        usage_key = str(self.scope_ids.usage_id)
        if not self.has_verified_tags and (verified_skills or ignored_skills):
            XBLOCK_SKILL_VERIFIED.send_event(
                time=datetime.now(timezone.utc),
                xblock_info=XBlockSkillVerificationData(
                    usage_key=usage_key,
                    verified_skills=verified_skills,
                    ignored_skills=ignored_skills,
                )
            )
            self.has_verified_tags = True

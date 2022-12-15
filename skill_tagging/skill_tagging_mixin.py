"""
A mixin that fetches and verifies skills related to an Xblock, that can be added for all XBlocks.
"""

import logging
from django.conf import settings
from django.utils.translation import gettext as _
from openedx_events.learning.data import XBlockSkillVerificationData
from openedx_events.learning.signals import XBLOCK_SKILL_VERIFIED
from urllib.parse import quote, urljoin
from xblock.core import XBlock
from xblock.fields import Boolean, Scope

from .utils import get_api_client

LOGGER = logging.getLogger(__name__)

# Make '_' a no-op so we can scrape strings
_ = lambda text: text


@XBlock.wants('user')
class SkillTaggingMixin:
    has_verified_tags = Boolean(
        display_name=_("Has verified tags"),
        default=False,
        help=_("Xblock has verified tags?"),
        scope=Scope.user_state
    )
    
    def _fetch_skill_tags(self):
        if hasattr(settings, 'TAXONOMY_API_BASE_URL'):
            API_BASE_URL = settings.TAXONOMY_API_BASE_URL
        else:
            API_BASE_URL = None

        if not API_BASE_URL:
            LOGGER.warning("Require TAXONOMY_API_BASE_URL to be present in the settings.")
            return

        user_service = self.runtime.service(self, 'user')
        if not user_service:
            LOGGER.info("No user service available for this xblock. Cannot proceed.")
            return

        user = user_service.get_current_user()
        api_client = get_api_client(user=user)

        usage_id_str = self.scope_ids.usage_id.__str__()
        XBLOCK_SKILL_TAGS_API = urljoin(
            API_BASE_URL,
            '/taxonomy/api/v1/xblocks/?usage_key={}'.format(quote(usage_id_str))
        )
        response = api_client.get(XBLOCK_SKILL_TAGS_API)
        response.raise_for_status()
        result = response.json()['results'][0]
        return result['skills']

    @XBlock.json_handler
    def fetch_tags(self, data, suffix=''):
        return self._fetch_skill_tags()

    @XBlock.json_handler
    def verify_tags(self, tags, suffix=''):
        usage_key = self.scope_ids.usage_id.__str__()
        verified_skill_ids = []
        ignored_skill_ids = []
        skills = self._fetch_skill_tags()
        for skill in skills:
            if skill['name'] in tags:
                verified_skill_ids.append(skill['id'])
            else:
                ignored_skill_ids.append(skill['id'])
        if not self.has_verified_tags:
            XBLOCK_SKILL_VERIFIED.send_event(
                xblock_info=XBlockSkillVerificationData(
                    usage_key=usage_key,
                    verified_skills=verified_skill_ids,
                    ignored_skills=ignored_skill_ids,
                )
            )
            self.has_verified_tags = True

"""
skill_tagging signal handlers
"""

from openedx_events.event_bus import get_producer
from openedx_events.learning.signals import XBLOCK_SKILL_VERIFIED


def listen_for_xblock_skill_verified(**kwargs):
    """
    Publish openedx-event XBLOCK_SKILL_VERIFIED signal onto the event bus.
    """
    get_producer().send(
        signal=XBLOCK_SKILL_VERIFIED,
        topic='xblock-skill-verified',
        event_key_field='xblock_info.usage_key',
        event_data={'xblock_info': kwargs['xblock_info']},
        event_metadata=kwargs['metadata'],
    )

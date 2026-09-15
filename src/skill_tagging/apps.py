"""
skill_tagging Django application initialization.
"""

from django.apps import AppConfig


class SkillTaggingConfig(AppConfig):
    """
    Configuration for the skill_tagging Django application.
    """

    name = 'skill_tagging'

    plugin_app = {
        "signals_config": {
            "lms.djangoapp": {
                "relative_path": "handlers",
                "receivers": [
                    {
                        "receiver_func_name": "listen_for_xblock_skill_verified",
                        "signal_path": "openedx_events.learning.signals.XBLOCK_SKILL_VERIFIED",
                    },
                ],
            }
        },
    }

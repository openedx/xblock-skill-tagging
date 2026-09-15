"""
Django app plugin for fetching and verifying tags for xblock skills.
"""
from importlib.metadata import version

__version__ = version("skill_tagging")

# pylint: disable=invalid-name
default_app_config = 'skill_tagging.apps.SkillTaggingConfig'

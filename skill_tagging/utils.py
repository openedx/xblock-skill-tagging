"""
Utility functions for SkillTaggingMixin
"""
import requests


def get_api_client(user):
    """
    Get the authenticated api client for user
    """
    # pylint: disable=import-error,import-outside-toplevel
    from edx_rest_api_client.auth import SuppliedJwtAuth
    from openedx.core.djangoapps.oauth_dispatch.jwt import create_jwt_for_user

    client = requests.Session()
    jwt = create_jwt_for_user(user)
    client.auth = SuppliedJwtAuth(jwt)
    return client

import requests
from openedx.core.djangoapps.oauth_dispatch.jwt import create_jwt_for_user
from edx_rest_api_client.auth import SuppliedJwtAuth


def get_api_client(user):
    client = requests.Session()
    jwt = create_jwt_for_user(user)
    client.auth = SuppliedJwtAuth(jwt)
    return client
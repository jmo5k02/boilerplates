import logging
from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakGetError

from settings import global_settings

logger = logging.getLogger(__name__)

async def get_authentication_client() -> KeycloakOpenID:
    """
    Get the authentication client.
    This client is only able to authenticate a user
    """
    try:
        yield KeycloakOpenID(
            server_url=global_settings.KC_SERVER_URL,
            client_id=global_settings.KC_AUTH_CLIENT_ID,
            realm_name=global_settings.KC_REALM_NAME,
            client_secret_key=global_settings.KC_AUTH_CLIENT_SECRET
        )
    except Exception as e:
        logger.error("Error while getting the authentication client: %s", e)


async def get_user_manager() -> KeycloakAdmin:
    """
    This function yields a KeycloakAdmin object that has the 
    necessary permissions to manage users in the Keycloak realm  
    This is used to create, update, delete and retrieve users
    """
    try:
        keycloak_openid: KeycloakOpenID = KeycloakOpenID(
            server_url=global_settings.KC_SERVER_URL,
            client_id=global_settings.KC_USER_MANAGER_CLIENT_ID,
            realm_name=global_settings.KC_REALM_NAME,
            client_secret_key=global_settings.KC_USER_MANAGER_CLIENT_SECRET,
            verify=True,
        )
        admin_token = keycloak_openid.token(grant_type="client_credentials")
        user_manager: KeycloakAdmin = KeycloakAdmin(
            server_url=global_settings.KC_SERVER_URL,
            realm_name=global_settings.KC_REALM_NAME,
            user_realm_name=global_settings.KC_REALM_NAME,
            client_id=global_settings.KC_USER_MANAGER_CLIENT_ID,
            client_secret_key=global_settings.KC_USER_MANAGER_CLIENT_SECRET,
            verify=True,
            token=admin_token
        )
    except KeycloakGetError as e:
        logger.error("KeycloakGetError: (%s), (%s)", str(e), type(e))
        # TODO Add proper error handling with maybe a custom exception and handlers
    yield user_manager
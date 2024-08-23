"""
This module holds all important dependencies for the application.
"""
import logging
from fastapi import Depends
from typing import Annotated

from sqlalchemy.orm import Session
from src.api_core.database import get_db

from keycloak import KeycloakOpenID, KeycloakAdmin
from src.auth.keycloak_clients import get_authentication_client, get_user_manager
from src.auth.schemas import TokenData
from src.users.models import User

from src.auth.security_utils import get_current_user_and_token

logger = logging.getLogger(__name__)

DbSession = Annotated[Session, Depends(get_db)]

# This dependency ensures that a KeycloakOpenID Client for user authentication will be made available to a function
GetAuthenticationClient = Annotated[KeycloakOpenID, Depends(get_authentication_client)]

# This dependency ensures that a KeycloakOpenID Client for user management will be made available to a function
GetUserManager = Annotated[KeycloakAdmin, Depends(get_user_manager)]

# This dependency ensures that the access_token (user information) from the client and the User object from the database
#  will be verified and made available to a function
CurrentUserAndToken = Annotated[tuple[TokenData, User], Depends(get_current_user_and_token)]
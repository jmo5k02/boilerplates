"""
This module holds all functions related to security with keycloak
"""

import logging
import requests
import jwt
from jwt import PyJWKClient
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from settings import global_settings
from src.api.database import get_db
from src.auth.schemas import TokenData
from src.users.models import User
from src.auth.exceptions import credentials_exception, attribute_exception

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")

jwks_client = PyJWKClient(global_settings.KC_CERTS_URL)

async def get_current_user_and_token(token: str = Depends(oauth2_scheme),
                                    session: Session = Depends(get_db)
                                    ) -> tuple[TokenData, User]:
    """
    This function verifies the clients jwt token and returns the user and token data
    """
    connection_exception = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Service currently unavailable. Please try again later.",
    )
    
    # First extract necessary information from the token
    username: str = ""
    roles: list[str] = []
    groups: list[str] = []
    try:
        key_pub = jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            jwt=token, key=key_pub, algorithms=[global_settings.JWT_ALGORITHM], audience="account"
        )
        logger.debug("Token payload: %s", payload)
        username: str = payload.get("preferred_username")
        if username is None:
            logger.info("User has no username in token")
            raise credentials_exception
        
        token_data = TokenData(email=username, roles=roles, groups=groups)

    except jwt.PyJWKClientConnectionError as e:
        logger.fatal("Failed to connect to Keycloak. Error: (%s), (%s)", str(e), type(e))
        raise connection_exception from e
    
    except jwt.PyJWTError as e:
        logger.exception("JWT Decode error %s", e)
        raise credentials_exception from e
    
    except AttributeError as e:
        logger.warning("JWT token is missing necessary attributes.\n%s\nPayload:%s ", e, payload)
        logger.warning("Check if user has a default group when created")
        raise attribute_exception from e
    
    # Now try to get the user from the database
    # The email==username so this works
    user = session.query(User).filter(User.email == username).first()
    if user is None:
        logger.warning("User %s not found in database", username)
        raise credentials_exception
    # TODO Add this to the user model
    # if not user.is_active:
    #     logger.info("User %s is inactive", username)
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return token_data, user
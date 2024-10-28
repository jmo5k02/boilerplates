import logging
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from app.settings import settings
from app.auth.models import AppUser
from app.db.deps import TenantDbSessionDep

logger = logging.getLogger(__name__)

# TokenDep is a dependency that returns the access token
reusable_oauth2 = OAuth2PasswordBearer(
  tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)
TokenDep = Annotated[str, Depends(reusable_oauth2)]

# CurrentUserDep is a dependency that returns the current user
async def get_current_user(session: TenantDbSessionDep, request: Request) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = await reusable_oauth2(request)
    print(session)
    print(token)
    # Try to decode the jwt
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("No username in token")
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        logger.error("Invalid token: %s", e)
        raise credentials_exception
    return token_data
CurrentUserDep = Annotated[AppUser, Depends(get_current_user)]
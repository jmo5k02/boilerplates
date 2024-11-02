import logging
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from app.auth.models import AppUser
from app.auth.schemas import UserTokenData
from app.plugins import plugins

logger = logging.getLogger(__name__)

# TokenDep is a dependency that returns the access token
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)
TokenDep = Annotated[str, Depends(reusable_oauth2)]


# CurrentUserDep is a dependency that returns the current user
async def get_current_user(request: Request) -> AppUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth_plugin = plugins.get("basic-auth-provider")
    token_data: UserTokenData = await auth_plugin.get_current_user(request)

    if not token_data:
        logger.warning("No token data")
        raise credentials_exception
    session: AsyncSession = request.state.db
    user = await session.execute(
        select(AppUser).where(AppUser.email == token_data.email)
    )
    user = user.scalar_one_or_none()
    if not user:
        logger.error(f"User {token_data.email} not found")
        raise credentials_exception

    return user

    # token = await reusable_oauth2(request)
    # session = request.state.db
    # print(session)
    # print(token)
    # # TODO Use auth plugins here to support multiple auth methods
    # # Try to decode the jwt
    # try:
    #     payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    #     email: str = payload.get("sub")
    #     if email is None:
    #         logger.error("No email in token")
    #         raise credentials_exception
    #     token_data = UserTokenData(email=email)
    # except InvalidTokenError as e:
    #     logger.error("Invalid token: %s", e)
    #     raise credentials_exception
    # return token_data


CurrentUserDep = Annotated[AppUser, Depends(get_current_user)]


async def get_current_user_role(request: Request, current_user: CurrentUserDep):
    return current_user.get_tenant_role(request.state.tenant)


CurrentUserRoleDep = Annotated[str, Depends(get_current_user_role)]

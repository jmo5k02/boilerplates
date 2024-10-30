import logging

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.plugins.bases.auth_provider import AuthProviderPlugin
from app.auth.schemas import UserTokenData
from app.settings import settings

log = logging.getLogger(__name__)

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

class BasicAuthProviderPlugin(AuthProviderPlugin):
    title = "Basic Auth Provider"
    slug = "basic-auth-provider"
    description = "Generic basic authentication provider with JWT and username and password"

    author = "Justus Mrosk"
    author_url = ""

    reusable_oauth2 = OAuth2PasswordBearer(
        tokenUrl=f"{settings.API_V1_STR}/login/access-token"
    )

    async def get_current_user(self, request: Request, **kwargs) -> UserTokenData:
        token = await self.reusable_oauth2(request)
        session = request.state.db

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                log.exception("No email in token")
                raise credentials_exception
            token_data = UserTokenData(email=email)
        except InvalidTokenError as e:
            log.exception("Invalid token: %s", e)
            raise credentials_exception
        except Exception as e:
            log.exception("Error decoding token: %s", e)
            raise credentials_exception
        return token_data
                

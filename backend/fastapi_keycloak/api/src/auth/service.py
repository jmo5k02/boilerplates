import logging
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from keycloak import KeycloakAdmin, KeycloakOpenID
from keycloak.exceptions import KeycloakPostError, KeycloakAuthenticationError, KeycloakConnectionError

from settings import global_settings
from src.users.service import UserService
from src.users.schema import UserCreate, UserOutput
from .schemas import Token

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, session: Session):
        self.user_service = UserService(session)

    async def register_user(self,
                            data: UserCreate,
                            user_manager: KeycloakAdmin
                            ) -> UserOutput:
        # TODO make the commented code work by creating missing functions
        # if await self.user_service.get_user_by_email(data.email):
        #     logger.exception("User (%s) that is already inside app database tried to register", data.email)
        #     raise ValueError("User already exists")
        # if await self.get_user_by_email(data.email):
        #     logger.exception("User (%s) that is already inside Keycloak database tried to register", data.email)
        #     raise ValueError("User already exists")
        try:
            user_id = await user_manager.a_create_user(
                {
                    "email": data.email,
                    "firstName": data.first_name,
                    "lastName": data.last_name,
                    "enabled": True,
                    "attributes" : {
                        "address" : data.address,
                    },
                    "credentials": [{"value": data.password,"type": "password"}],
                },
                exist_ok=False
            )
        except KeycloakPostError as e:
            logger.exception("KeycloakPostError: (%s)", e.error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Could not create user!") from e
        except Exception as e:
            logger.fatal("Unknown Error: (%s) (%s)", str(e), type(e))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail="Internal Server Error") from e
        logger.info("User created in keycloak: (%s)", user_id)
        logger.info("Creating user in database: (%s)", data.email)
        try:
            user: UserOutput|None = await self.user_service.create_user(data, kc_user_id=user_id)
        except Exception as e:
            logger.fatal("Unknown Error: (%s) (%s)", str(e), type(e))
            logger.warning("User not created in the database. Deleting user from keycloak.")
            await user_manager.a_delete_user(user_id)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Error creating user. Email or username is already taken!") from e
        logger.info("User created in database: (%s)", user.email)
        if global_settings.VERIFY_EMAIL:
            response = await user_manager.a_send_verify_email(user_id=user_id)
            print(response)
        return user
    
    async def login_user_and_return_token(self,
                                          form_data: OAuth2PasswordRequestForm,
                                          kc_openid_auth_client: KeycloakOpenID
                                          ) -> Token:
        # TODO check if user is already in the database
        # user = await self.user_repo.get_user_by_email(form_data.username)
        # if not user:
        #     logger.info("User not found: (%s)", form_data.username)
        #     raise credentials_exception
        # Now request the access token from keycloak
        try:
            response = await kc_openid_auth_client.a_token(form_data.username, form_data.password)
        except KeycloakConnectionError as e:
            logger.fatal("KeycloakConnectionError: {%s}", e.error_message)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service is currently unavailable. Please try again later.",
            ) from e
        except KeycloakAuthenticationError as e:
            logger.info("KeycloakAuthenticationError: {%s}", e.error_message)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            ) from e
        # except Exception as e:
        #     logger.error("Unkown Error: (%s), (%s)", str(e), type(e))
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Internal server error",
        #     ) from e
        return Token(access_token=response["access_token"], token_type="Bearer")
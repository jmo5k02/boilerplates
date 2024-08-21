from pydantic import BaseModel

class Token(BaseModel):
    """
    This schema is used to define the token response sent to the client
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    This schema defines the token data that can be extracted from the jwt token
    The Token data will be user information extracted from the jwt token
    """
    email: str | None = None
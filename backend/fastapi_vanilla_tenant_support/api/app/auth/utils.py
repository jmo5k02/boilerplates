from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import jwt
from passlib.context import CryptContext

from app.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
  """Create the access token the client can use to authenticate against the backend"""
  expire = datetime.now(timezone.utc) + expires_delta
  to_encode = {"exp": expire, "sub": str(subject)}
  encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  return encoded_jwt


def create_signed_url(file_id: str, expires_in: int = 3600) -> str:
  """Create a signed URL for the client to view an image from the serve endpoint"""
  token = create_access_token(file_id, timedelta(seconds=expires_in))
  query_params = urlencode({"token": token})
  return f"{settings.API_V1_STR}/files/{file_id}/serve?{query_params}"


def verify_password(plain_password: bytes, hashed_password: bytes, salt: bytes) -> bool:
  plain_password = plain_password + salt
  return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: bytes) -> bytes:
  print(password)
  return bytes(pwd_context.hash(password), "utf-8")

from fastapi.responses import JSONResponse
from fastapi import HTTPException, status

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
)

attribute_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Your user account is not properly configured. Please contact your administrator.",
    )
from typing import Annotated

from fastapi import Depends

from app.settings import Settings, get_settings
SettingsDep = Annotated[Settings, Depends(get_settings)]

from sqlalchemy.ext.asyncio import AsyncSession
from app.src.api_core.db.database import get_db
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
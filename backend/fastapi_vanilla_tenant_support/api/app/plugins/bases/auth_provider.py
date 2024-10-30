from app.plugins.base import Plugin
from fastapi.requests import Request

class AuthProviderPlugin(Plugin):
    type = "auth_provider"

    def get_current_user(self, request: Request, **kwargs):
        raise NotImplementedError
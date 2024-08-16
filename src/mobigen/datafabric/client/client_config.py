from typing import Optional, List, Callable

from pydantic import BaseModel


class ConfigModel(BaseModel):
    class Config:
        extra = "forbid"


class ClientConfig(ConfigModel):
    base_url: str
    api_version: Optional[str] = "v1"
    retry: Optional[int] = 3
    retry_wait: Optional[int] = 30
    retry_codes: List[int] = [429, 504]
    auth_token: Optional[Callable] = None
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    auth_header: Optional[str] = None
    extra_headers: Optional[dict] = None
    auth_token_mode: Optional[str] = "Bearer"

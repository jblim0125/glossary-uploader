from typing import Optional, Dict

from pydantic.v1 import Extra, Field, BaseModel


class ExtraHeaders(BaseModel):
    __root__: Optional[Dict[str, str]] = None


class ServerConnection(BaseModel):
    class Config:
        extra = Extra.forbid

    hostPort: str = Field(
        ...,
        description='Server Config. Must include API end point ex: http://localhost:8080/api',
    )
    apiVersion: Optional[str] = Field(
        'v1', description='Server API version to use.'
    )
    jwtToken: Optional[str] = Field(
        None, description='JWT Token for Authentication.'
    )
    enableVersionValidation: Optional[bool] = Field(
        True, description='Validate Server & Client Version.'
    )
    limitRecords: Optional[int] = Field(
        '1000', description='Limit the number of records for Indexing.'
    )
    forceEntityOverwriting: Optional[bool] = Field(
        False, description='Force the overwriting of any entity.'
    )
    extraHeaders: Optional[ExtraHeaders] = Field(None, title='Extra Headers')

import os
from typing import TypeVar

from pydantic.v1 import BaseModel

T = TypeVar("T", bound=BaseModel)


class URL(str):
    """
    Handle URL for creds retrieval

    Args:
        value (tuple):

    Attributes:
        value (value):
    """

    def __new__(cls, *value):
        """
        note: we use *value and v0 to allow an empty URL string
        """
        if value:
            url = value[0]
            if not isinstance(url, (URL, str)):
                raise TypeError(f'Unexpected type for URL: "{type(url)}"')
            if not (
                    url.startswith("http://")
                    or url.startswith("https://")
                    or url.startswith("ws://")
                    or url.startswith("wss://")
            ):
                raise ValueError(
                    f'Passed string value "{url}" is not an'
                    f' "http*://" or "ws*://" URL'
                )
        return str.__new__(cls, *value)


def get_api_version(api_version: str) -> str:
    """
    Get version API

    Args:
        api_version (str):
    Returns:
         str
    """
    if api_version is None:
        api_version = os.environ.get("API_VERSION")
    if api_version is None:
        api_version = "v1"

    return api_version

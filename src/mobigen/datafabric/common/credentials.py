import os
from typing import Tuple

import dateutil.parser

Credentials = Tuple[str, str, str]


class DATE(str):
    """
    date string in the format YYYY-MM-DD
    """

    def __new__(cls, value):
        if not value:
            raise ValueError("Unexpected empty string")
        if not isinstance(value, str):
            raise TypeError(f'Unexpected type for DATE: "{type(value)}"')
        if value.count("-") != 2:
            raise ValueError(
                f"Unexpected date structure. expected " f'"YYYY-MM-DD" got {value}'
            )
        try:
            dateutil.parser.parse(value)
        except Exception as exc:
            msg = f"{value} is not a valid date string: {exc}"
            raise ValueError(msg)

        return str.__new__(cls, value)


class FLOAT(str):
    """
    api allows passing floats or float as strings.
    let's make sure that param passed is one of the two, so we don't pass
    invalid strings all the way to the servers.
    """

    def __new__(cls, value):
        if isinstance(value, (float, int)):
            return value
        if isinstance(value, str):
            return float(value.strip())

        raise ValueError(f'Unexpected float format "{value}"')


def get_credentials(
    key_id: str = None, secret_key: str = None, oauth: str = None
) -> Credentials:
    """
    Get credentials

    Args:
        key_id (str):
        secret_key (str):
        oauth (oauth):
    Returns:
        Credentials
    """
    oauth = oauth or os.environ.get("API_OAUTH_TOKEN")

    key_id = key_id or os.environ.get("API_KEY_ID")
    if key_id is None and oauth is None:
        raise ValueError(
            "Key ID must be given to access Alpaca trade API",
            " (env: API_KEY_ID)",
        )

    secret_key = secret_key or os.environ.get("API_SECRET_KEY")
    if secret_key is None and oauth is None:
        raise ValueError(
            "Secret key must be given to access Alpaca trade API"
            " (env: API_SECRET_KEY"
        )

    return key_id, secret_key, oauth



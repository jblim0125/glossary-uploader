import re
import string
from typing import Union, Type, Any, TypeVar

from pydantic.v1 import BaseModel

T = TypeVar("T", bound=BaseModel)


def format_name(name: str) -> str:
    """
    Given a name, replace all special characters by `_`
    :param name: name to format
    :return: formatted string
    """
    subs = re.escape(string.punctuation + " ")
    return re.sub(r"[" + subs + "]", "_", name)


# pylint: disable=too-many-return-statements
def get_entity_type(
    entity: Union[Type[T], str],
) -> str:
    """
    Given an Entity T, return its type.
    E.g., Table returns table, Dashboard returns dashboard...

    Also allow to be the identity if we just receive a string
    """
    if isinstance(entity, str):
        return entity
    class_name: str = entity.__name__.lower()
    return class_name


def model_str(arg: Any) -> str:
    """
    Default model stringifying method.

    Some elements such as FQN, EntityName, UUID
    have the actual value under the pydantic base __root__
    """
    if hasattr(arg, "__root__"):
        return str(arg.__root__)

    return str(arg)

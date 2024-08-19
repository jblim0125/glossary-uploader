"""
Generic models
"""
from enum import Enum
from typing import TypeVar

from pydantic import BaseModel

# Entities are instances of BaseModel
Entity = BaseModel
T = TypeVar("T")


class PublicDataStandardSheetNames(Enum):
    COMMON_STANDARD_TERMINOLOGY = "공통표준용어"
    COMMON_STANDARD_WORD = "공통표준단어"

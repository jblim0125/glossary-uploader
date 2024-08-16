"""
Generic models
"""
from typing import TypeVar

from pydantic import BaseModel

# Entities are instances of BaseModel
Entity = BaseModel
T = TypeVar("T")

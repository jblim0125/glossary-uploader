import os
from abc import ABC, abstractmethod
from functools import singledispatchmethod

import pandas as pd
from enum import Enum
from pydantic.v1 import Extra, Field, BaseModel

from mobigen.datafabric.utils.logger import cli_logger


class SourceType(Enum):
    EXCEL = 'EXCEL'
    CSV = 'CSV'


class GlossarySourceConfig(BaseModel):
    class Config:
        extra = Extra.forbid

    source_type: SourceType = Field(
        default=SourceType.EXCEL,
        description='Type of source file. Default is Excel.',
    )
    file_path: str = Field(
        ...,
        description='Path to the source file.',
    )


class DataFrameReader(ABC):
    # Init
    def __init__(self, source_config: GlossarySourceConfig):
        self.source = source_config
        self.file_exists_check()

    # Exists Check
    def file_exists_check(self):
        if not os.path.exists(self.source.file_path):
            raise FileNotFoundError(f'File not found: {self.source.file_path}')

    @abstractmethod
    def read_excel(self, **kwargs):
        pass

    @abstractmethod
    def read_csv(self, **kwargs):
        pass

import pandas as pd

from mobigen.datafabric.reader.base import DataFrameReader, GlossarySourceConfig, SourceType
from mobigen.datafabric.utils.logger import cli_logger

logger = cli_logger()


class ExcelDataFrameReader(DataFrameReader):
    def __init__(self, source: GlossarySourceConfig):
        self.source = source
        super().__init__(source)

    def read_csv(self, **kwargs):
        pass

    def read_excel(self, sheet_name: str) -> pd.DataFrame:
        return pd.read_excel(self.source.file_path, sheet_name=sheet_name)


if __name__ == '__main__':
    source_config = GlossarySourceConfig(
        source_type=SourceType.EXCEL,
        file_path='/Users/jblim/Downloads/공공데이터 공통표준용어(2023.11월)_수정/공공데이터 공통표준용어(2023.11월)_수정.xlsx'
    )

    reader = ExcelDataFrameReader(source_config)
    df = reader.read_excel(sheet_name='공통표준용어')

    header = ''
    for col in df.columns:
        header = header + col + ','

    logger.info(header)

    for index, row in df.iterrows():
        row_str = ''
        for col in df.columns:
            """ newline character 제거 """
            row_str = row_str + str(row[col]).replace('\n', ' ') + ','
        logger.info(f"[{index}] : {row_str}")

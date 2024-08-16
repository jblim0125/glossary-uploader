import signal
import sys
from enum import IntEnum
from typing import Optional, Sequence, Any, List

from generated.schema.api.data.createGlossaryTerm import CreateGlossaryTermRequest
from generated.schema.entity.data.glossary import Glossary
from mobigen.datafabric.client.api import APIS
from mobigen.datafabric.client.server_config import ServerConnection
from mobigen.datafabric.reader.base import GlossarySourceConfig, SourceType
from mobigen.datafabric.reader.excel_file_reader import ExcelDataFrameReader
from mobigen.datafabric.utils.logger import cli_logger

JWT = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlzQm90IjpmYWxzZSwiaXNzIjoib3Blbi1tZXRhZGF0YS5vcmciLCJpYXQiOjE2NjM5Mzg0NjIsImVtYWlsIjoiYWRtaW5Ab3Blbm1ldGFkYXRhLm9yZyJ9.tS8um_5DKu7HgzGBzS1VTA5uUjKWOCU0B_j08WXBiEC0mr0zNREkqVfwFDD-d24HlNEbrqioLsBuFRiwIWKc1m_ZlVQbG7P36RUxhuv2vbSp80FKyNM-Tj93FDzq91jsyNmsQhyNv_fNr3TXfzzSPjHt8Go0FMMP66weoKMgW2PbXlhVKwEuXUHyakLLzewm9UMeQaEiRzhiTMU3UkLXcKbYEJJvfNFcLwSl9W8JCO_l0Yj3ud-qt_nQYEZwqW6u5nfdQllN133iikV4fM5QZsMCnm8Rq1mvLR0y9bmJiD7fwM1tmJ791TUWqmKaTnP49U493VanKpUAfzIiOiIbhg"

logger = cli_logger()


class Exit(IntEnum):
    """Exit reasons."""
    OK = 0
    ERROR = 1
    KeyboardInterrupt = 2


def sig_int_handler(_: int, __: Any) -> None:  # pragma: no cover
    exit(Exit.OK)


signal.signal(signal.SIGINT, sig_int_handler)


class Main:

    api: APIS

    """Main class."""
    def start(self, args: Optional[Sequence[str]] = None) -> Exit:
        """Main function."""
        logger.debug("API Client Test Start")
        api = APIS(ServerConnection(
            hostPort="http://192.168.105.51:8585/api",
            apiVersion="v1",
            jwtToken=JWT,
        ))
        glossary = api.get_by_name(Glossary, "PublicDataStandards")
        logger.info(f"Glossary: {glossary}")

        reader = ExcelDataFrameReader(GlossarySourceConfig(
            source_type=SourceType.EXCEL,
            file_path="/Users/jblim/Downloads/공공데이터 공통표준용어(2023.11월)_수정/공공데이터 공통표준용어(2023.11월)_수정.xlsx"
        ))
        df = reader.read_excel(sheet_name="공통표준용어")

        if df is None:
            logger.error("Failed to read excel file")
            return self.finish(Exit.ERROR)

        # logger.info(f"Header: {df.columns}")
        for index, row in df.iterrows():
            logger.info(f"[{index}] : {row}")
            req = self.create_glossary_term_request(df.columns, row)
            logger.info(f"Create Glossary Term req: {req}")
            res = api.create_or_update(req)
            logger.info(f"Create Glossary Term Res: {res}")

        # request: CreateGlossaryRequest = CreateGlossaryRequest(
            #     name="test",
            #     description="test",
            #     columns=[],
            #     data=df.to_dict(orient="records"),
            # )

        logger.info("API Client Test End")
        self.finish(Exit.OK)
        # return Exit.ERROR

    def create_glossary_term_request(self, columns: List[str], row) -> CreateGlossaryTermRequest:
        req = CreateGlossaryTermRequest()
        for column in enumerate(columns):
            if column == "공통표준용어명":
                req.name = row[column]
                req.displayName = row[column]
            elif column == "공통표준용어설명":
                req.description = row[column]
            elif column == "공통표준용어영문약어명":
                req.synonyms.clear()
                req.synonyms.append(row[column])


        req = CreateGlossaryTermRequest(
            name=row[columns[0]],
            description=row[columns[1]],
            synonyms=[row[columns[2]]],
            antonyms=[row[columns[3]]],
            related_terms=[row[columns[4]]],
            domain=row[columns[5]],
            category=row[columns[6]],
            source=row[columns[7]],
            reference=row[columns[8]],
            status=row[columns[9]],
            version=row[columns[10]],
            owner=row[columns[11]],
            created_by=row[columns[12]],
            created_at=row[columns[13]],
            updated_by=row[columns[14]],
            updated_at=row[columns[15]],
        )
        return req

    def finish(self, error) -> Exit:
        self.api.close()
        return error


if __name__ == '__main__':
    main: Main = Main()
    sys.exit(main.start())

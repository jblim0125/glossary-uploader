import signal
import sys
from enum import IntEnum
from typing import Optional, Sequence, Any, List
import argparse

from generated.schema.api.data.createGlossary import CreateGlossaryRequest
from generated.schema.api.data.createGlossaryTerm import CreateGlossaryTermRequest
from generated.schema.entity.data.glossary import Glossary
from generated.schema.entity.data.glossaryTerm import GlossaryTerm
from mobigen.datafabric.client.api import APIS
from mobigen.datafabric.client.server_config import ServerConnection
from mobigen.datafabric.models import common
from mobigen.datafabric.reader.base import GlossarySourceConfig, SourceType
from mobigen.datafabric.reader.excel_file_reader import ExcelDataFrameReader
from mobigen.datafabric.utils.logger import cli_logger
from mobigen.datafabric.glossary_term.glossary_term import MakeGlossaryTerm

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
    """Main class."""

    api: APIS
    glossary: Glossary

    def init_server(self, server: str):
        logger.debug("Init DataFabric API Client")
        self.api = APIS(ServerConnection(
            hostPort=f"{server}/api",
            apiVersion="v1",
            jwtToken=JWT,
        ))
        if self.api.health_check():
            logger.info("DataFabric API Client Initialized")
        else:
            logger.error("DataFabric API Client Initialization Failed")
            sys.exit(Exit.ERROR)

    def init_glossary(self, name: str, display_name: str = None, desc: str = None):
        """Create Glossary"""

        logger.debug(f"Find Glossary: {name}")
        find_glossary = self.api.get_by_name(Glossary, name)
        if find_glossary is not None:
            logger.info(f"Glossary Already Exists: {name}")
            self.glossary = find_glossary
            return

        create_glossary = CreateGlossaryRequest(
            name=name,
            displayName=display_name,
            description=desc,
        )
        logger.info(f"Create Glossary: {create_glossary}")
        res_glossary = self.api.create_or_update(create_glossary)
        if res_glossary is not None:
            logger.debug(f"Glossary : {res_glossary}")
            self.glossary = res_glossary
            return

        raise Exception(f"Init(Find or Create) Glossary Fail: {name}")

    def upload_terms(self,
                     sheet_name: str,
                     source_type: str,
                     file_path: str = 'glossary/2023_11_public_data_standard.xlsx'):

        source_config = GlossarySourceConfig(
            source_type=SourceType.CSV if source_type == "csv" else SourceType.EXCEL,
            file_path=file_path
        )
        logger.info(f"Type: {source_config.source_type}, Path: {source_config.file_path}")

        reader = ExcelDataFrameReader(source_config)

        df = reader.read_excel(sheet_name=sheet_name)

        if df is None:
            logger.error(f"Failed To Read Excel File. "
                         f"Type: {source_config.source_type}, Path: {source_config.file_path}, "
                         f"SheetName: {sheet_name}")
            return self.finish(Exit.ERROR)

        # logger.info(f"Header: {df.columns}")
        for index, row in df.iterrows():
            """ Print Row Value """
            debug_str = f"Index[{index}]: "
            for row_index, row_value in row.items():
                row_value = str(row_value).strip(" ").replace("\n", " ")
                if row_index == len(row) - 1:
                    debug_str += f"{row_value}"
                    continue
                debug_str += f"{row_value}, "
            logger.debug(debug_str)

            """ Skip Empty Row """
            if row['번호'] is None or str(row['번호']).strip(" ").strip("\n") == "":
                logger.debug(f"Skip Empty Row")
                continue

            """ Create Glossary Term Request """
            term = MakeGlossaryTerm(
                glossary_fqn=self.glossary.fullyQualifiedName.__root__,
                sheet_name=sheet_name,
                columns=df.columns,
                row=row,
            )
            if term.get_term() is None:
                logger.debug("Skip Empty Term")
                continue
            logger.info(f"Create Glossary Term: {index}: {term.get_term().name}, {term.get_term().synonyms}")
            logger.debug(f"Glossary Term Detail: {term.get_term().__str__()}")
            try:
                self.api.create_or_update(term.get_term())
                # res: GlossaryTerm = self.api.create_or_update(term.get_term())
                # logger.debug(f"Create Glossary Term Res: {res.id}, {res.name}")
            except Exception as e:
                logger.error(f"Error: {e}")
                continue

        return self.finish(Exit.OK)

    def finish(self, error) -> Exit:
        self.api.close()
        return error

    def delete_all_glossary(self, name):
        logger.info(f"Delete All Glossary: {name}")
        self.finish(Exit.OK)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="DataFabric Glossary Uploader Client")

    root_parser = parser.add_subparsers(dest='command', required=True, help='Sub-command to execute')

    """ Create Glossary """
    parser_init = root_parser.add_parser('init', help='Initialize the glossary')
    parser_init.add_argument('-s', '--server',
                             type=str, required=True,
                             help='URL of the data fabric server (e.g., http://datafabric:8080)')
    parser_init.add_argument('-n', '--name',
                             type=str, required=True, help='Glossary name')
    parser_init.add_argument('--display_name',
                             type=str, required=True, help='glossary display name')
    parser_init.add_argument('--desc',
                             type=str, required=True, help='glossary description')

    """ Create or Update Glossary Terms """
    parser_upload = root_parser.add_parser('upload', help='Create or Update Glossary Terms')
    parser_upload.add_argument('-s', '--server',
                               type=str, required=True,
                               help='URL of the data fabric server (e.g., http://datafabric:8080)')
    parser_upload.add_argument('-n', '--name',
                               type=str, required=True, help='glossary name')
    parser_upload.add_argument('-t', '--type',
                               type=str, choices=['CSV', 'EXCEL'],
                               required=True, help='Type of the file (CSV or EXCEL)')
    parser_upload.add_argument('-p', '--path',
                               type=str, required=True, help='Path to the file')
    parser_upload.add_argument('--sheet_name', type=str, required=False,
                               help='If the file is an Excel file, specify the sheet name')

    """ Delete All Glossary """
    parser_delete_all = root_parser.add_parser('delete_all', help='Delete All Resource Glossary')
    parser_delete_all.add_argument('-s', '--server',
                                   type=str, required=True,
                                   help='URL of the data fabric server (e.g., http://datafabric:8080)')
    parser_delete_all.add_argument('-n', '--name',
                                   type=str, required=True, help='glossary name')

    # 명령줄 인자 파싱
    args = parser.parse_args()

    # 명령에 따른 처리
    if args.command == 'init':
        print(f"Initializing Glossary "
              f"server: {args.server}, "
              f"glossary name: {args.name}, "
              f"glossary display name : {args.display_name}, "
              f"glossary description: {args.desc}")
    elif args.command == 'upload':
        print(f"Create Or Update Glossary Terms "
              f"server: {args.server}, "
              f"glossary name: {args.name}, "
              f"resource type: {args.type}, "
              f"resource path: {args.path}")
    elif args.command == 'delete_all':
        print(f"Delete All Glossary"
              f"server: {args.server}, "
              f"glossary name: {args.name}")

    arg_dict = vars(args)

    main: Main = Main()
    main.init_server(arg_dict['server'])

    if arg_dict['command'] == 'init':
        main.init_glossary(
            name=arg_dict['name'],
            display_name=arg_dict['display_name'],
            desc=arg_dict['desc'])
    elif arg_dict['command'] == 'upload':
        main.init_glossary(name=arg_dict['name'])
        main.upload_terms(
            source_type=arg_dict['type'],
            file_path=arg_dict['path'],
            sheet_name=arg_dict['sheet_name'])
    elif arg_dict['command'] == 'delete_all':
        main.delete_all_glossary(name=arg_dict['name'])

    # sys.exit(main.start(args))

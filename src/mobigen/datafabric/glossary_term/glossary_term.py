from enum import Enum
from typing import List

from generated.schema.api.data.createGlossaryTerm import CreateGlossaryTermRequest
from mobigen.datafabric.models import common


class CommonStandardTerminologyColumnNames(Enum):
    TERMINOLOGY = "공통표준용어명"
    DESC = "공통표준용어설명"
    ENGLISH_ABBREVIATION = "공통표준용어영문약어명"
    ACCEPTABLE_VALUE = "허용값"
    RELEVANT_ORGANIZATION = "소관기관명"
    SYNONYM_LIST = "용어 이음동의어 목록"


class CommonStandardWordColumnNames(Enum):
    NAME = "공통표준단어명"
    ENGLISH_ABBREVIATION = "공통표준단어영문약어명"
    ENGLISH_NAME = "공통표준단어 영문명"
    DESC = "공통표준단어 설명"
    # "형식단어 여부"
    # "공통표준도메인분류명"
    SYNONYM_LIST = "이음동의어 목록"
    FORBIDDEN_WORDS = "금칙어 목록"


class MakeGlossaryTerm:
    term: CreateGlossaryTermRequest

    def __init__(self, glossary_fqn: str, sheet_name: str, columns: List[str], row):
        self.term = CreateGlossaryTermRequest(
            glossary=glossary_fqn,
            name="initialize",
            displayName="initialize",
            description="initialize",
        )
        if sheet_name == common.PublicDataStandardSheetNames.COMMON_STANDARD_TERMINOLOGY.value:
            for column in columns:
                if row[column] is None:
                    continue
                if column == CommonStandardTerminologyColumnNames.TERMINOLOGY.value:
                    data = str(row[column]).strip(" ").strip("\n")
                    self.term.name = data
                    self.term.displayName = data
                    continue
                if column == CommonStandardTerminologyColumnNames.DESC.value:
                    data = str(row[column]).strip(" ").strip("\n")
                    self.term.description = data
                    continue
                if column == CommonStandardTerminologyColumnNames.ENGLISH_ABBREVIATION.value:
                    data = str(row[column]).strip(" ").strip("\n")
                    self.term.synonyms = []
                    self.term.synonyms.append(data)
                    continue
                if column == CommonStandardTerminologyColumnNames.SYNONYM_LIST.value:
                    data = str(row[column]).strip(" ").strip("\n")
                    if data == "-":
                        continue
                    if self.term.synonyms is None:
                        self.term.synonyms = []

                    if "," in data:
                        synonym_list = data.split(",")
                        for synonym in synonym_list:
                            synonym = synonym.strip(" ").strip("\n")
                            self.term.synonyms.append(synonym)
                    else:
                        self.term.synonyms.append(data)

        elif sheet_name == common.PublicDataStandardSheetNames.COMMON_STANDARD_WORD.value:
            for column in enumerate(columns):
                if column == CommonStandardWordColumnNames.NAME:
                    self.term.name = row[column]
                    self.term.displayName = row[column]
                elif column == CommonStandardWordColumnNames.DESC:
                    self.term.description = row[column]
                elif column == CommonStandardWordColumnNames.ENGLISH_ABBREVIATION:
                    self.term.synonyms.clear()
                    self.term.synonyms.append(row[column])
                elif column == CommonStandardWordColumnNames.SYNONYM_LIST:
                    self.term.relatedTerms.clear()
                    self.term.relatedTerms.append(row[column])

    def get_term(self) -> CreateGlossaryTermRequest:
        return self.term

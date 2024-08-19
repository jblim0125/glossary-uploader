# 데이터 패브릭 데이터 사전 업로더 개발자 가이드

## 개요

데이터 패브릭 사전 업로더의 개발자 가이드입니다.

## 개발 환경

- Python 3.10 이상  
- git
- make
- datamodel_code_generator
- 데이터 패브릭 API 스키마 데이터  

## 최초 환경 설정  

1. JSON 데이터 다운로드  

    ```shell
    git clone https://github.com/DataFabricTech/ingestion.git ingestion
    ```

2. Generate Python code  

    ```shell
    make generate
    ```

3. Pydantic Error Fix
    JSON 파일로부터 생성된 Python 파일에서 Pydantic 에러가 발생. 다음 명령어를 실행하여 오류를 import 를 수정합니다.
    
    ```shell
    find ./src/generated -name "*.py" -type f -exec sed -i '' 's/from pydantic import/from pydantic.v1 import/g' {} +
    ```

## 디렉토리 별 설명

- `src/` : Python 코드가 위치한 디렉토리  
- `src/generated/` : 데이터 패브릭 API 스키마로부터 생성된 Python 코드가 위치한 디렉토리  
- `src/client/` : 데이터 패브릭 API 클라이언트 코드가 위치한 디렉토리  
- `src/common` : 공통 모듈이 위치한 디렉토리  
- `src/glossary_term` : 용어집 업로드를 위한 메시지 생성 코드가 위치한 디렉토리  
- `src/models` : 데이터 모델 디렉토리  
- `src/reader` : EXCEL, CSV 파일을 읽는 코드가 위치한 디렉토리  
- `src/utils` : 유틸리티 코드가 위치한 디렉토리  
- `script/` : 데이터 패브릭 JSON 스키마로부터 Python 코드를 생성하는 스크립트가 위치한 디렉토리  

## 동작 설명

- 기본 동작  

    1. 서버 접속 정보를 기반으로 데이터 패브릭 API 클라이언트를 생성합니다.
    2. 업로드할 데이터를 읽어서 데이터 모델로 변환합니다.
    3. 데이터 모델을 데이터 패브릭 API 클라이언트를 이용하여 업로드합니다.
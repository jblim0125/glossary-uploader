from setuptools import setup, find_packages

setup(
    name="datafabric-glossary-uploader",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # 패키지 의존성 리스트 (예: "numpy>=1.18.0", "pandas>=1.1.0")
        "pandas==2.2.2",
        "datamodel-code-generator==0.25.9",
        "openpyxl==3.1.5",
        "requests==2.32.3",
    ],
    entry_points={
        'console_scripts': [
            # 'command_name = package.module:function',
        ],
    },
    author="jblim",
    author_email="irisdev@mobigen.com",
    description="공공데이터 표준 정보(EXCEL 파일)를 데이터패브릭 용어 사전으로 업로드하는 프로세스",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/datafabrictech/glossary-uploader",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='==3.10',
)

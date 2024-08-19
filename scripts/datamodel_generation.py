#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
This script generates the Python models from the JSON Schemas definition. Additionally, it replaces the `SecretStr`
pydantic class used for the password fields with the `CustomSecretStr` pydantic class which retrieves the secrets
from a configured secrets' manager.
"""

import os

from datamodel_code_generator.__main__ import main

current_directory = os.getcwd()
dest_path = "./src"

UTF_8 = "UTF-8"
UNICODE_REGEX_REPLACEMENT_FILE_PATHS = [
    f"{dest_path}/generated/schema/entity/classification/tag.py",
    f"{dest_path}/generated/schema/entity/events/webhook.py",
    f"{dest_path}/generated/schema/entity/teams/user.py",
    f"{dest_path}/generated/schema/entity/type.py",
    f"{dest_path}/generated/schema/type/basic.py",
]

args = f"--input ./ingestion/spec/src/main/resources/json/schema --input-file-type jsonschema --output {dest_path}/generated/schema --set-default-enum-member".split(" ")

print("datamodel_code_generator: %s" % args)

main(args)

for file_path in UNICODE_REGEX_REPLACEMENT_FILE_PATHS:
    print("Processing file:", file_path)
    with open(file_path, "r", encoding=UTF_8) as file_:
        content = file_.read()
        # Python now requires to move the global flags at the very start of the expression
        content = content.replace("(?U)", "(?u)")
    with open(file_path, "w", encoding=UTF_8) as file_:
        file_.write(content)


# Until https://github.com/koxudaxi/datamodel-code-generator/issues/1895
MISSING_IMPORTS = [f"{dest_path}/generated/schema/entity/applications/app.py", ]
WRITE_AFTER = "from __future__ import annotations"

for file_path in MISSING_IMPORTS:
    with open(file_path, "r", encoding=UTF_8) as file_:
        lines = file_.readlines()
    with open(file_path, "w", encoding=UTF_8) as file_:
        for line in lines:
            file_.write(line)
            if line.strip() == WRITE_AFTER:
                file_.write("from typing import Union  # custom generate import\n\n")

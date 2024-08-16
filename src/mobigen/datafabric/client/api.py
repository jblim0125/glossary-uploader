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
OpenMetadata is the high level Python API that serves as a wrapper
for the metadata-server API. It is based on the generated pydantic
models from the JSON schemas and provides a typed approach to
working with OpenMetadata entities.
"""
import logging
import traceback
from typing import Dict, Iterable, List, Optional, Type, TypeVar, Union

from pydantic.v1 import BaseModel
from pydantic.v1.json import pydantic_encoder
from requests.compat import quote

from generated.schema.type import basic
from generated.schema.type.basic import FullyQualifiedEntityName
from generated.schema.type.entityReference import EntityReference
from mobigen.datafabric.client.apis.server_apis import ServerApis
from mobigen.datafabric.client.auth_provider import AuthenticationProvider
from mobigen.datafabric.client.client import Client, APIError
from mobigen.datafabric.client.client_config import ClientConfig
from mobigen.datafabric.client.models import EntityList
from mobigen.datafabric.client.routes import ROUTES
from mobigen.datafabric.client.server_config import ServerConnection
from mobigen.datafabric.utils.logger import rest_logger
from mobigen.datafabric.utils.utils import model_str, get_entity_type

logger = rest_logger()

# The naming convention is T for Entity Types and C for Create Types
T = TypeVar("T", bound=BaseModel)
C = TypeVar("C", bound=BaseModel)


class MissingEntityTypeException(Exception):
    """
    We are receiving an Entity Type[T] not covered
    in our suffix generation list
    """


class InvalidEntityException(Exception):
    """
    We receive an entity not supported in an operation
    """


class EmptyPayloadException(Exception):
    """
    Raise when receiving no data, even if no exception
    during the API call is received
    """


class APIS(
    ServerApis,
):
    """
    Generic interface to the Data Fabric API

    It is a polymorphism on all our different Entities.

    Specific functionalities to be inherited from apis
    """

    client: Client
    _auth_provider: AuthenticationProvider
    config: ServerConnection

    class_root = ".".join(["src", "generated", "schema"])
    entity_path = "entity"
    api_path = "api"
    data_path = "data"

    def __init__(
            self,
            config: ServerConnection,
    ):
        self.config = config

        self._auth_provider = AuthenticationProvider.create(self.config.jwtToken)

        client_config: ClientConfig = ClientConfig(
            base_url=self.config.hostPort,
            api_version=self.config.apiVersion,
            auth_header="Authorization",
            extra_headers=self.config.extraHeaders,
            auth_token=self._auth_provider.get_access_token,
        )
        self.client = Client(client_config)
        if self.config.enableVersionValidation:
            if self.health_check() is False:
                raise Exception("Server is not available")

    @staticmethod
    def get_suffix(entity: Type[T]) -> str:
        """
        Given an entity Type from the generated sources,
        return the endpoint to run requests.
        """

        route = ROUTES.get(entity.__name__)
        if route is None:
            raise MissingEntityTypeException(
                f"Missing {entity} type when generating suffixes"
            )

        return route

    @staticmethod
    def get_module_path(entity: Type[T]) -> str:
        """
        Based on the entity, return the module path
        it is found inside generated
        """
        return entity.__module__.split(".")[-2]

    def get_create_entity_type(self, entity: Type[T]) -> Type[C]:
        """
        imports and returns the Create Type from an Entity Type T.
        We are following the expected path structure to import
        on-the-fly the necessary class and pass it to the consumer
        """
        file_name = f"create{entity.__name__}"

        class_path = ".".join(
            [self.class_root, self.api_path, self.get_module_path(entity), file_name]
        )

        class_name = f"Create{entity.__name__}Request"
        create_class = getattr(
            __import__(class_path, globals(), locals(), [class_name]), class_name
        )
        return create_class

    @staticmethod
    def update_file_name(create: Type[C], file_name: str) -> str:
        """
        Update the filename for services and schemas
        """
        if "service" in create.__name__.lower():
            return file_name.replace("service", "Service")

        if "schema" in create.__name__.lower():
            return file_name.replace("schema", "Schema")

        return file_name

    def get_entity_from_create(self, create: Type[C]) -> Type[T]:
        """
        Inversely, import the Entity type based on the create Entity class
        """

        class_name = create.__name__.replace("Create", "").replace("Request", "")
        file_name = (
            class_name.lower()
            .replace("glossaryterm", "glossaryTerm")
        )
        class_path = ".".join(
            filter(
                None,
                [
                    self.class_root,
                    self.entity_path if not file_name.startswith("test") else None,
                    self.get_module_path(create),
                    self.update_file_name(create, file_name),
                ],
            )
        )
        entity_class = getattr(
            __import__(class_path, globals(), locals(), [class_name]), class_name
        )
        return entity_class

    def _create(self, data: C, method: str) -> T:
        """
        Internal logic to run POST vs. PUT
        """
        entity = data.__class__
        is_create = "create" in data.__class__.__name__.lower()

        # Prepare the return Entity Type
        if is_create:
            entity_class = self.get_entity_from_create(entity)
        else:
            raise InvalidEntityException(
                f"PUT operations need a CreateEntity, not {entity}"
            )

        fn = getattr(self.client, method)
        resp = fn(self.get_suffix(entity), data=data.json(encoder=pydantic_encoder))
        if not resp:
            raise EmptyPayloadException(
                f"Got an empty response when trying to PUT to {self.get_suffix(entity)}, {data.json()}"
            )
        return entity_class(**resp)

    def create_or_update(self, data: C) -> T:
        """Run a PUT requesting via create request C"""
        return self._create(data=data, method="put")

    def create(self, data: C) -> T:
        """Run a POST requesting via create request C"""
        return self._create(data=data, method="post")

    def get_by_name(
            self,
            entity: Type[T],
            fqn: Union[str, FullyQualifiedEntityName],
            fields: Optional[List[str]] = None,
            nullable: bool = True,
    ) -> Optional[T]:
        """
        Return entity by name or None
        """

        return self._get(
            entity=entity,
            path=f"name/{quote(model_str(fqn), safe='')}",
            fields=fields,
            nullable=nullable,
        )

    def get_by_id(
            self,
            entity: Type[T],
            entity_id: Union[str, basic.Uuid],
            fields: Optional[List[str]] = None,
            nullable: bool = True,
    ) -> Optional[T]:
        """
        Return entity by ID or None
        """
        return self._get(
            entity=entity,
            path=model_str(entity_id),
            fields=fields,
            nullable=nullable,
        )

    def _get(
            self,
            entity: Type[T],
            path: str,
            fields: Optional[List[str]] = None,
            nullable: bool = True,
    ) -> Optional[T]:
        """
        Generic GET operation for an entity
        :param entity: Entity Class
        :param path: URL suffix by FQN or ID
        :param fields: List of fields to return
        """
        fields_str = "?fields=" + ",".join(fields) if fields else ""
        try:
            resp = self.client.get(f"{self.get_suffix(entity)}/{path}{fields_str}")
            if not resp:
                raise EmptyPayloadException(
                    f"Got an empty response when trying to GET from {self.get_suffix(entity)}/{path}{fields_str}"
                )
            return entity(**resp)
        except APIError as err:
            # We can expect some GET calls to return us a None and manage it in following steps.
            # No need to pollute the logs in these cases.
            if err.code == 404 and nullable:
                return None

            # Any other API errors will be passed to the client
            logger.debug(traceback.format_exc())
            logger.debug(
                "GET %s for %s. Error %s - %s",
                entity.__name__,
                path,
                err.status_code,
                err,
            )
            raise err

    def get_entity_reference(
            self, entity: Type[T], fqn: str
    ) -> Optional[EntityReference]:
        """
        Helper method to obtain an EntityReference from
        a FQN and the Entity class.
        :param entity: Entity Class
        :param fqn: Entity instance FQN
        :return: EntityReference or None
        """
        instance = self.get_by_name(entity, fqn)
        if instance:
            return EntityReference(
                id=instance.id,
                type=get_entity_type(entity),
                fullyQualifiedName=model_str(instance.fullyQualifiedName),
                description=instance.description,
                href=instance.href,
            )
        logger.debug("Cannot find the Entity %s", fqn)
        return None

    # pylint: disable=too-many-locals
    def list_entities(
            self,
            entity: Type[T],
            fields: Optional[List[str]] = None,
            after: Optional[str] = None,
            limit: int = 100,
            params: Optional[Dict[str, str]] = None,
            skip_on_failure: bool = False,
    ) -> EntityList[T]:
        """
        Helps us paginate over the collection
        """

        suffix = self.get_suffix(entity)
        url_limit = f"?limit={limit}"
        url_after = f"&after={after}" if after else ""
        url_fields = f"&fields={','.join(fields)}" if fields else ""
        resp = self.client.get(
            path=f"{suffix}{url_limit}{url_after}{url_fields}", data=params
        )

        if skip_on_failure:
            entities = []
            for elmt in resp["data"]:
                try:
                    entities.append(entity(**elmt))
                except Exception as exc:
                    logger.error(
                        f"Error creating entity [{entity.__name__}]. Failed with exception {exc}"
                    )
                    logger.debug(
                        f"Can't create [{entity.__name__}] from [{elmt}]. Skipping."
                    )
                    continue
        else:
            entities = [entity(**elmt) for elmt in resp["data"]]

        total = resp["paging"]["total"]
        after = resp["paging"]["after"] if "after" in resp["paging"] else None
        return EntityList(entities=entities, total=total, after=after)

    def list_all_entities(
            self,
            entity: Type[T],
            fields: Optional[List[str]] = None,
            limit: int = 100,
            params: Optional[Dict[str, str]] = None,
            skip_on_failure: bool = False,
    ) -> Iterable[T]:
        """
        Utility method that paginates over all EntityLists
        to return a generator to fetch entities
        :param entity: Entity Type, such as Table
        :param fields: Extra fields to return
        :param limit: Number of entities in each pagination
        :param params: Extra parameters, e.g., {"service": "serviceName"} to filter
        :return: Generator that will be yielding all Entities
        """

        # First batch of Entities
        entity_list = self.list_entities(
            entity=entity,
            fields=fields,
            limit=limit,
            params=params,
            skip_on_failure=skip_on_failure,
        )
        for elem in entity_list.entities:
            yield elem

        after = entity_list.after
        while after:
            entity_list = self.list_entities(
                entity=entity,
                fields=fields,
                limit=limit,
                params=params,
                after=after,
                skip_on_failure=skip_on_failure,
            )
            for elem in entity_list.entities:
                yield elem
            after = entity_list.after

    def delete(
            self,
            entity: Type[T],
            entity_id: Union[str, basic.Uuid],
            recursive: bool = False,
            hard_delete: bool = False,
    ) -> None:
        """
        API call to delete an entity from entity ID

        Args
            entity (T): entity Type
            entity_id (basic.Uuid): entity ID
        Returns
            None
        """
        url = f"{self.get_suffix(entity)}/{model_str(entity_id)}"
        url += f"?recursive={str(recursive).lower()}"
        url += f"&hardDelete={str(hard_delete).lower()}"
        self.client.delete(url)

    def health_check(self) -> bool:
        """
        Run version api call. Return `true` if response is not None
        """
        raw_version = self.client.get("/system/version")["version"]
        logger.info("Server version: %s", raw_version)
        return raw_version is not None

    def close(self):
        """
        Closing connection

        Returns
            None
        """
        self.client.close()

import boto3
import io
import logging
from botocore.exceptions import ClientError
from typing import Iterable, Optional
from pulumi_aws import s3
from pulumi import Resource as PulumiResource

from damavand import utils
from damavand.resource import BaseObjectStorage
from damavand.resource.resource import buildtime, runtime
from damavand.errors import (
    CallResourceBeforeProvision,
    RuntimeException,
    ObjectNotFound,
    ResourceAccessDenied,
)


logger = logging.getLogger(__name__)


class AwsBucket(BaseObjectStorage):
    def __init__(
        self,
        name,
        region: str,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, id_, tags, **kwargs)
        self.__s3_client = boto3.client("s3", region_name=region)

    @buildtime
    def provision(self):
        if not self.id_:
            self.id_ = self.name
            logger.info(
                f"Resource ID not provided for bucket with name `{self.name}`, using the name as ID."
            )

        self._pulumi_object = s3.Bucket(
            self.id_,
            bucket=self.name,
            tags=self.tags,
            **self.extra_args,
        )

    @runtime
    def write(self, object: bytes, path: str):
        try:
            self.__s3_client.put_object(
                Body=object,
                Bucket=self.name,
                Key=path,
            )
        except ClientError as e:
            match utils.error_code_from_boto3(e):
                case "AccessDenied" | "403":
                    raise ResourceAccessDenied(name=self.name)
                case _:
                    logger.exception("Failed to write the object to AWS.")
                    raise RuntimeException()

    @runtime
    def read(self, path: str) -> bytes:
        try:
            buffer = io.BytesIO()
            self.__s3_client.download_fileobj(
                Bucket=self.name, Key=path, Fileobj=buffer
            )

            return buffer.getvalue()
        except ClientError as e:
            match utils.error_code_from_boto3(e):
                case "AccessDenied" | "403":
                    raise ResourceAccessDenied(name=self.name)
                case "NoSuchKey" | "404":
                    raise ObjectNotFound(name=path)
                case _:
                    logger.exception("Failed to read the object from AWS")
                    raise RuntimeException()

    @runtime
    def delete(self, path: str):
        try:
            self.__s3_client.delete_object(Bucket=self.name, Key=path)
        except ClientError as e:
            match utils.error_code_from_boto3(e):
                case "AccessDenied" | "403":
                    raise ResourceAccessDenied(name=self.name)
                case _:
                    logger.exception("Failed to delete the object from AWS.")
                    raise RuntimeException()

    @runtime
    def list(self) -> Iterable[str]:
        """
        Return an iterable of object keys in the bucket.

        __ATTENTION__: This method is expensive for large buckets as it request multiple times to fetch all objects.
        """
        try:
            paginator = self.__s3_client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.name):
                for obj in page.get("Contents", []):
                    yield obj["Key"]
        except ClientError as e:
            match utils.error_code_from_boto3(e):
                case "AccessDenied" | "403":
                    raise ResourceAccessDenied(name=self.name)
                case _:
                    logger.exception("Failed to list objects from AWS.")
                    raise RuntimeException()

    @runtime
    def exist(self, path: str) -> bool:
        """Check if an object exists in the bucket."""
        try:
            self.__s3_client.head_object(Bucket=self.name, Key=path)
            return True
        except ClientError as e:
            match utils.error_code_from_boto3(e):
                case "NoSuchKey" | "404":
                    return False
                case "AccessDenied" | "403":
                    raise ResourceAccessDenied(name=self.name)
                case _:
                    logger.exception("Failed to check the object existence in AWS.")
                    raise RuntimeException()

    @buildtime
    def to_pulumi(self) -> PulumiResource:
        if self._pulumi_object is None:
            raise CallResourceBeforeProvision()

        return self._pulumi_object

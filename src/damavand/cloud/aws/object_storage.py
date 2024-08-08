from functools import cache
import boto3
import io
import logging
from botocore.exceptions import ClientError
from typing import Iterable, Optional
from pulumi_aws import s3
from pulumi import Resource as PulumiResource

from damavand import utils
from damavand.controllers import ObjectStorageController, buildtime, runtime
from damavand.errors import (
    RuntimeException,
    ObjectNotFound,
    ResourceAccessDenied,
)


logger = logging.getLogger(__name__)


class AwsObjectStorageController(ObjectStorageController):
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
    @cache
    def resource(self) -> PulumiResource:
        return s3.BucketV2(
            resource_name=f"{self.name}-bucket",
            bucket_prefix=self.name,
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
                    raise ResourceAccessDenied(name=self.name) from e
                case _:
                    raise RuntimeException() from e

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
                    raise ResourceAccessDenied(name=self.name) from e
                case "NoSuchKey" | "404":
                    raise ObjectNotFound(name=path) from e
                case _:
                    raise RuntimeException() from e

    @runtime
    def delete(self, path: str):
        try:
            self.__s3_client.delete_object(Bucket=self.name, Key=path)
        except ClientError as e:
            match utils.error_code_from_boto3(e):
                case "AccessDenied" | "403":
                    raise ResourceAccessDenied(name=self.name) from e
                case _:
                    raise RuntimeException() from e

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
                    raise ResourceAccessDenied(name=self.name) from e
                case _:
                    raise RuntimeException() from e

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
                    raise ResourceAccessDenied(name=self.name) from e
                case _:
                    raise RuntimeException() from e

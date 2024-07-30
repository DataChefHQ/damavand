import boto3
import logging
from botocore.exceptions import ClientError
from typing import Optional
from pulumi_aws import s3
from pulumi import Resource as PulumiResource

from damavand.resource import BaseObjectStorage
from damavand.resource.resource import buildtime, runtime


logger = logging.getLogger(__name__)


class AwsBucket(BaseObjectStorage):
    def __init__(
        self,
        name,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, id_, tags, **kwargs)
        self.__s3_client = boto3.client("s3")

    @buildtime
    def provision(self):
        if not self.id_:
            self.id_ = self.name
            logger.info(
                f"Resource ID not provided for bucket with name `{self.name}`, using the name as ID."
            )

        self.__pulumi_object = s3.Bucket(
            self.id_,
            bucket=self.name,
            tags=self.tags,
            **self.extra_args,
        )

    @runtime
    def add_object(self, object: bytes, path: str):
        try:
            self.__s3_client.put_object(
                Body=object,
                Bucket=self.name,
                Key=path,
            )
        except ClientError as e:
            logger.error(f"Failed to add object to bucket `{self.name}`: {e}")

    @buildtime
    def to_pulumi(self) -> PulumiResource:
        if not self.__pulumi_object:
            raise ValueError(
                "Resource not provisioned yet. Call `provision` method first."
            )

        return self.__pulumi_object

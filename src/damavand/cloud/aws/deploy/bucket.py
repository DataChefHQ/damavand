import boto3
import logging
from botocore.exceptions import ClientError
from typing import Optional
from cdktf import TerraformStack, TerraformResource
from cdktf_cdktf_provider_aws.s3_bucket import S3Bucket

from damavand.resource import IBucket
from damavand.resource.resource import buildtime, runtime
from damavand.stage import ResourceStage


logger = logging.getLogger(__name__)


class AwsBucket(IBucket):
    def __init__(
        self,
        name,
        stack: TerraformStack,
        stage: ResourceStage,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, stack, stage, id_, tags, **kwargs)
        self.__s3_client = boto3.client("s3")

    @buildtime
    def provision(self):
        if not self.id_:
            self.id_ = self.name
            logger.info(
                f"Resource ID not provided for bucket with name `{self.name}`, using the name as ID."
            )

        self.__cdktf_object = S3Bucket(
            self.stack,
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
    def to_cdktf(self) -> TerraformResource:
        if not self.__cdktf_object:
            raise ValueError(
                "Resource not provisioned yet. Call `provision` method first."
            )

        return self.__cdktf_object

import logging
from typing import Optional
from functools import cache

import boto3

from sparkle.application import Sparkle
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from damavand.base.controllers import SparkController, buildtime
from damavand.cloud.aws.resources import GlueComponent, GlueComponentArgs
from damavand.cloud.aws.resources.glue_component import GlueJobDefinition
from damavand.errors import BuildtimeException
try:
    from awsglue.context import GlueContext
except ImportError:
    logging.warning("Could not import GlueContext. This is expected if running locally.")


logger = logging.getLogger(__name__)


class AwsSparkController(SparkController):
    def __init__(
        self,
        name,
        region: str,
        applications: list[Sparkle] = [],
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        super().__init__(name, applications, id_, tags, **kwargs)
        self._glue_client = boto3.client("glue", region_name=region)

        self.applications = applications

    @property
    @buildtime
    @cache
    def resource(self) -> GlueComponent:
        if not self.applications:
            raise BuildtimeException("No applications found to create Glue jobs.")

        return GlueComponent(
            name=self.name,
            args=GlueComponentArgs(
                jobs=[
                    GlueJobDefinition(
                        name=app.config.app_name,
                        description=app.config.__doc__ or "",
                    )
                    for app in self.applications
                ],
            ),
        )

    def default_cloud_session(self) -> SparkSession:
        """Return the default Spark session for a Glue job.

        Returns:
            SparkSession: The Spark session.
        """

        warehouse_location = self.resource.iceberg_bucket.bucket

        GLUE_CONFIG = {
            "spark.sql.extensions": ",".join(self._spark_extensions),
            "spark.sql.catalog.glue_catalog": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.glue_catalog.catalog-impl": "org.apache.iceberg.aws.glue.GlueCatalog",
            "spark.sql.catalog.glue_catalog.io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
            "spark.sql.catalog.glue_catalog.warehouse": warehouse_location,
            "spark.sql.jsonGenerator.ignoreNullFields": False,
        }

        spark_conf = SparkConf()

        for key, value in GLUE_CONFIG.items():
            spark_conf.set(key, str(value))

        glue_context = GlueContext(SparkContext.getOrCreate(conf=spark_conf))
        return glue_context.spark_session

import os
import logging
from typing import Optional
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession

from damavand.environment import Environment
from damavand.controllers import ApplicationController
from damavand.controllers.base_controller import runtime

# TODO: The following import will be moved to a separated framework
from damavand.sparkle.models import Trigger
from damavand.sparkle.core import Sparkle
from damavand.sparkle.data_reader import DataReader
from damavand.sparkle.data_writer import DataWriter


logger = logging.getLogger(__name__)


class SparkController(ApplicationController, Sparkle):
    def __init__(
        self,
        name,
        reader: DataReader,
        writer: DataWriter,
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:
        ApplicationController.__init__(self, name, id_, tags, **kwargs)
        Sparkle.__init__(self, reader=reader, writer=writer)

    @property
    def _spark_extensions(self) -> list[str]:
        return [
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        ]

    @property
    def _spark_packages(self) -> list[str]:
        return [
            "org.apache.iceberg:iceberg-spark-runtime-3.2_2.12:1.3.1",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0",
            "org.apache.spark:spark-avro_2.12:3.3.0",
        ]

    @property
    def default_local_session(self) -> SparkSession:
        """Return the default local Spark session."""

        ivy_settings_path = os.environ.get("IVY_SETTINGS_PATH", None)
        LOCAL_CONFIG = {
            "spark.sql.extensions": ",".join(self._spark_extensions),
            "spark.jars.packages": ",".join(self._spark_packages),
            "spark.sql.jsonGenerator.ignoreNullFields": False,
            "spark.sql.session.timeZone": "UTC",
            "spark.sql.catalog.spark_catalog": "org.apache.iceberg.spark.SparkSessionCatalog",
            "spark.sql.catalog.spark_catalog.type": "hive",
            "spark.sql.catalog.local": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.local.type": "hadoop",
            "spark.sql.catalog.local.warehouse": "/tmp/warehouse",
            "spark.sql.defaultCatalog": "local",
        }

        spark_conf = SparkConf()

        for key, value in LOCAL_CONFIG.items():
            spark_conf.set(key, str(value))

        spark_session = (
            # NOTE: Pyright does not work `@classproperty` decorator used in `SparkSession`. This however should be fixed in pyspark v4.
            SparkSession.builder.master("local[*]")  # type: ignore
            .appName("LocalDataProductApp")
            .config(conf=spark_conf)
        )

        if ivy_settings_path:
            spark_session.config("spark.jars.ivySettings", ivy_settings_path)

        return spark_session.getOrCreate()

    @property
    def default_cloud_session(self) -> SparkSession:
        """Return the default cloud Spark session."""

        raise NotImplementedError

    @property
    def default_session(self) -> SparkSession:
        """Return the currently active Spark session."""
        env = Environment.from_system_env()
        match env:
            case Environment.LOCAL:
                return self.default_local_session
            case _:
                return self.default_cloud_session

    def _get_spark_session(self, env: Environment) -> SparkSession:
        if env == Environment.LOCAL:
            raise NotImplementedError
        else:
            raise NotImplementedError

    @runtime
    def run(self, trigger: Trigger, session: Optional[SparkSession] = None) -> None:
        """Run the Spark application with the given trigger and session."""

        if session:
            Sparkle.run(self, trigger, session)
        else:
            Sparkle.run(self, trigger, self.default_session)

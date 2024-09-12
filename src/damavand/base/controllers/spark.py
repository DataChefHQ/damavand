import os
import logging
from typing import Optional
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession

from damavand.environment import Environment
from damavand.base.controllers import ApplicationController
from damavand.base.controllers.base_controller import runtime

from sparkle.application import Sparkle


logger = logging.getLogger(__name__)


class SparkController(ApplicationController):
    """
    The SparkController class is the base class for all Spark controllers
    implementations for each cloud provider.

    ...

    Attributes
    ----------
    name : str
        the name of the controller.
    applications : list[Sparkle]
        the list of Spark applications.
    id_ : Optional[str]
        the ID of the controller.
    tags : dict[str, str]
        the tags of the controller.
    kwargs : dict
        the extra arguments.

    Methods
    -------
    default_local_session()
        Return the default local Spark session.
    default_cloud_session()
        Return the default cloud Spark session.
    default_session()
        Return the currently active Spark session.
    application_with_id(app_id)
        Return the Spark application with the given ID.
    run_application(app_id)
        Run the Spark application with the given ID.
    """

    def __init__(
        self,
        name,
        applications: list[Sparkle] = [],
        id_: Optional[str] = None,
        tags: dict[str, str] = {},
        **kwargs,
    ) -> None:

        print("the value of _id is: ", id_)
        ApplicationController.__init__(
            self,
            name=name,
            id_=id_,
            tags=tags,
            **kwargs
        )

        self.applications: list[Sparkle] = applications

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

    def default_local_session(self) -> SparkSession:
        """Return the default local Spark session.

        Returns:
            SparkSession: The Spark session.
        """

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

    def default_cloud_session(self) -> SparkSession:
        """Return the default Spark session provided by the cloud spark machine.

        Returns:
            SparkSession: The Spark session.
        """

        raise NotImplementedError

    def default_session(self) -> SparkSession:
        """Return the currently active Spark session. If the environment is local, it
        returns the local session. Otherwise, it returns the cloud session.

        Returns:
            SparkSession: The Spark session.
        """
        env = Environment.from_system_env()
        match env:
            case Environment.LOCAL:
                return self.default_local_session()
            case _:
                return self.default_cloud_session()

    def application_with_id(self, app_id: str) -> Sparkle:
        """Return the Spark application with the given ID.

        Args:
            app_id (str): The application ID.

        Returns:
            Sparkle: The Spark application.
        """

        for app in self.applications:
            if app.config.app_id == app_id:
                return app

        raise ValueError(f"Application with ID {app_id} not found.")

    @runtime
    def run_application(self, app_id: str) -> None:
        """Run the Spark application with the given ID.

        Args:
            app_id (str): The application ID.
        """

        app = self.application_with_id(app_id)
        df = app.process()
        app.write(df)

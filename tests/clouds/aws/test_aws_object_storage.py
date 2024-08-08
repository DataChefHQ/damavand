import boto3
import pytest
from _pytest.monkeypatch import MonkeyPatch
from moto import mock_aws

from pulumi_aws import s3
from damavand.cloud.aws import AwsObjectStorageController
from damavand.errors import CallResourceBeforeProvision, ObjectNotFound


@pytest.fixture
@mock_aws
def bucket():
    return AwsObjectStorageController("test-bucket", region="us-east-1")


@pytest.fixture
@mock_aws
def conn():
    return boto3.resource("s3", region_name="us-east-1")


def test_to_pulumi_raise_before_provision(
    monkeypatch: MonkeyPatch, bucket: AwsObjectStorageController
):
    monkeypatch.setattr("damavand.utils.is_building", lambda: True)

    with pytest.raises(CallResourceBeforeProvision):
        bucket.to_pulumi()


def test_to_pulumi_return_pulumi_s3_bucket(
    monkeypatch: MonkeyPatch, bucket: AwsObjectStorageController
):
    monkeypatch.setattr("damavand.utils.is_building", lambda: True)

    bucket.provision()
    assert isinstance(bucket.to_pulumi(), s3.Bucket)


@mock_aws
def test_write(bucket: AwsObjectStorageController, conn):
    conn.create_bucket(Bucket=bucket.name)

    bucket.write(b"Hello, World!", "test.txt")

    obj = conn.Object(bucket.name, "test.txt")
    assert obj.get()["Body"].read() == b"Hello, World!"


@mock_aws
def test_read(bucket: AwsObjectStorageController, conn):
    conn.create_bucket(Bucket=bucket.name)

    obj = conn.Object(bucket.name, "test.txt")
    obj.put(Body=b"Hello, World!")

    assert bucket.read("test.txt") == b"Hello, World!"


@mock_aws
def test_read_not_exist(bucket: AwsObjectStorageController, conn):
    conn.create_bucket(Bucket=bucket.name)

    with pytest.raises(ObjectNotFound):
        bucket.read("test-not-exist.txt")


@mock_aws
def test_delete(bucket: AwsObjectStorageController, conn):
    conn.create_bucket(Bucket=bucket.name)

    obj = conn.Object(bucket.name, "test.txt")
    obj.put(Body=b"Hello, World!")

    bucket.delete("test.txt")

    with pytest.raises(conn.meta.client.exceptions.ClientError):
        obj.get()


@mock_aws
def test_exist(bucket: AwsObjectStorageController, conn):
    conn.create_bucket(Bucket=bucket.name)

    obj = conn.Object(bucket.name, "test.txt")
    obj.put(Body=b"Hello, World!")

    assert bucket.exist("test.txt")
    assert not bucket.exist("not-exist.txt")


@mock_aws
def test_list(bucket: AwsObjectStorageController, conn):
    conn.create_bucket(Bucket=bucket.name)

    conn.Object(bucket.name, "test1.txt").put(Body=b"Hello, World!")
    conn.Object(bucket.name, "test2.txt").put(Body=b"Hello, World!")
    conn.Object(bucket.name, "test3.txt").put(Body=b"Hello, World!")

    assert set(bucket.list()) == {"test1.txt", "test2.txt", "test3.txt"}

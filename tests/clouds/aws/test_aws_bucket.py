import boto3
import pytest
from _pytest.monkeypatch import MonkeyPatch
from moto import mock_aws

from pulumi_aws import s3
from damavand.cloud.aws import AwsBucket
from damavand.errors import BuildtimeError


@pytest.fixture
@mock_aws
def bucket():
    return AwsBucket("test-bucket", region="us-east-1")


@pytest.fixture
@mock_aws
def conn():
    return boto3.resource("s3", region_name="us-east-1")


def test_to_pulumi_raise_before_provision(monkeypatch: MonkeyPatch, bucket: AwsBucket):
    monkeypatch.setattr("damavand.utils.is_building", lambda: True)

    with pytest.raises(BuildtimeError):
        bucket.to_pulumi()


def test_to_pulumi_return_pulumi_s3_bucket(monkeypatch: MonkeyPatch, bucket: AwsBucket):
    monkeypatch.setattr("damavand.utils.is_building", lambda: True)

    bucket.provision()
    assert isinstance(bucket.to_pulumi(), s3.Bucket)


@mock_aws
def test_write(bucket: AwsBucket, conn):
    conn.create_bucket(Bucket=bucket.name)

    bucket.write(b"Hello, World!", "test.txt")

    obj = conn.Object(bucket.name, "test.txt")
    assert obj.get()["Body"].read() == b"Hello, World!"


@mock_aws
def test_read(bucket: AwsBucket, conn):
    conn.create_bucket(Bucket=bucket.name)

    obj = conn.Object(bucket.name, "test.txt")
    obj.put(Body=b"Hello, World!")

    assert bucket.read("test.txt") == b"Hello, World!"


@mock_aws
def test_delete(bucket: AwsBucket, conn):
    conn.create_bucket(Bucket=bucket.name)

    obj = conn.Object(bucket.name, "test.txt")
    obj.put(Body=b"Hello, World!")

    bucket.delete("test.txt")

    with pytest.raises(conn.meta.client.exceptions.ClientError):
        obj.get()


@mock_aws
def test_exist(bucket: AwsBucket, conn):
    conn.create_bucket(Bucket=bucket.name)

    obj = conn.Object(bucket.name, "test.txt")
    obj.put(Body=b"Hello, World!")

    assert bucket.exist("test.txt")
    assert not bucket.exist("not-exist.txt")


@mock_aws
def test_list(bucket: AwsBucket, conn):
    conn.create_bucket(Bucket=bucket.name)

    conn.Object(bucket.name, "test1.txt").put(Body=b"Hello, World!")
    conn.Object(bucket.name, "test2.txt").put(Body=b"Hello, World!")
    conn.Object(bucket.name, "test3.txt").put(Body=b"Hello, World!")

    assert set(bucket.list()) == {"test1.txt", "test2.txt", "test3.txt"}

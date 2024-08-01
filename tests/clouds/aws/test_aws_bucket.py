import pytest
from _pytest.monkeypatch import MonkeyPatch

from pulumi_aws import s3
from damavand.cloud.aws import AwsBucket
from damavand.errors import BuildtimeError


@pytest.fixture
def bucket():
    return AwsBucket("test-bucket")


def test_to_pulumi_raise_before_provision(monkeypatch: MonkeyPatch, bucket: AwsBucket):
    monkeypatch.setattr("damavand.utils.is_building", lambda: True)

    with pytest.raises(BuildtimeError):
        bucket.to_pulumi()


def test_to_pulumi_return_pulumi_s3_bucket(monkeypatch: MonkeyPatch, bucket: AwsBucket):
    monkeypatch.setattr("damavand.utils.is_building", lambda: True)

    bucket.provision()
    assert isinstance(bucket.to_pulumi(), s3.Bucket)

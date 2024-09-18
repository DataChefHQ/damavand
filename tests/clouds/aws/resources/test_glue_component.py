import json
import pytest
from typing import Optional, Tuple, List

import pulumi
import pulumi_aws as aws
from pulumi.runtime.mocks import MockResourceArgs, MockCallArgs

from damavand.cloud.aws.resources.glue_component import GlueJobDefinition


# NOTE: this has to be defined before importing infrastructure codes.
# Check Pulumi's documentation for more details: https://www.pulumi.com/docs/using-pulumi/testing/unit/
class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: MockResourceArgs) -> Tuple[Optional[str], dict]:
        return (args.name + "_id", args.inputs)

    def call(self, args: MockCallArgs) -> Tuple[dict, Optional[List[Tuple[str, str]]]]:
        return ({}, None)


pulumi.runtime.set_mocks(
    MyMocks(),
    preview=False,  # Sets the flag `dry_run`, which is true at runtime during a preview.
)

from damavand.cloud.aws.resources import GlueComponent, GlueComponentArgs  # noqa: E402


@pytest.fixture
def glue_component():
    return GlueComponent(
        name="test",
        args=GlueComponentArgs(
            jobs=[
                GlueJobDefinition(
                    name="test",
                    description="test",
                ),
                GlueJobDefinition(
                    name="test-reprocess",
                    description="test reporcess",
                ),
            ]
        ),
    )


@pulumi.runtime.test
def test_execution_role(glue_component):
    def should_have_one(roles: list[aws.iam.Role]):
        assert len(roles) == 1

    def should_name_have_prefix(names):
        name = names[0]
        assert name.startswith("test")

    def should_have_managed_arns(arnslists: list[list[str]]):
        arns = arnslists[0]
        assert len(arns) > 0
        assert set(arns).issubset(set(glue_component.managed_policy_arns))

    def should_assume_glue_service(assume_policies: list[str]):
        assume_policy = json.loads(assume_policies[0])
        assert {
            "Effect": "Allow",
            "Principal": {
                "Service": "glue.amazonaws.com",
            },
            "Action": "sts:AssumeRole",
        } in assume_policy["Statement"]

    pulumi.Output.all(glue_component.role).apply(should_have_one)
    pulumi.Output.all(glue_component.role.name).apply(should_name_have_prefix)
    pulumi.Output.all(glue_component.role.managed_policy_arns).apply(
        should_have_managed_arns
    )
    pulumi.Output.all(glue_component.role.assume_role_policy).apply(
        should_assume_glue_service
    )


@pulumi.runtime.test
def test_glue_jobs(glue_component):
    def should_have_two(jobslists: list[list[aws.glue.Job]]):
        jobs = jobslists[0]
        assert len(jobs) == 2

    def should_name_have_prefix(names: list[str]):
        name = names[0]
        assert name.startswith("test")

    pulumi.Output.all(glue_component.jobs).apply(should_have_two)
    for job in glue_component.jobs:
        pulumi.Output.all(job.name).apply(should_name_have_prefix)

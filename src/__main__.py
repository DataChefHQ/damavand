from damavand.core import CloudConnection


cloud = CloudConnection.from_aws_provider(
    "my-app",
    region="eu-west-1",
)

my_bucket = cloud.resource_factory.new_object_storage(
    "my-lovely-bucket-for-testing-damavand",
    tags={"owner": "kiarash@datachef.co"},
)


cloud.run()

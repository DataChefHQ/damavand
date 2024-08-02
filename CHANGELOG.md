## v0.3.0 (2024-08-02)

### Feat

- **tags**: add support for default and user/global tags
- **errors**: option to provide custom message to an exception
- **object_storage**: improved the error handlings
- **object_storage**: method to validate existance of an object
- **object_storage**: add list objects method
- **object_storage**: add delete method
- output running mode as warning log
- **aws, object_storage**: add read method

### Fix

- **provider**: setted properties were not directly available
- **object_storage**: not having access to original boto3 ClientError
- **object_storage**: not catching boto errors with http codes
- **resource_factory**: validate if aws provider has a region
- **object_storage**: align runtime region with buildtime region

### Refactor

- using custom error for build time errors
- rename bucket module name to object_storage

## v0.2.0 (2024-07-31)

### Fix

- rename cdktf_object to pulumi
- removing manual test codes

### Refactor

- replacing pulumi with cdktf

## v0.1.0 (2024-07-26)

### Feat

- add pytest depenencies.
- add mypy.
- add flask server
- init commit

### Fix

- missing boto3 stubs.
- version configuration and license in pyproject.toml.
- CI errors.

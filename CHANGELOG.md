## v0.4.1 (2024-10-03)

### Refactor

- update Sparkle lib
- remove creating Spark session from Damavand & refactor to follow Sparkle interfaces

## v0.4.0 (2024-09-24)

### Feat

- **llm**: extracting api access policies for easier customization
- **llm**: add api deployment and integration with sagemaker endpoint
- **llm**: add public access to the model
- **llm**: initiate the resource component for the vllm
- **sparkle**: revert to app_id to prevent confusions
- **pyspark**: integrating with sparkle
- **spark**: add azure implementations
- restructure to match the ARC Pattern
- spark added
- implementing the ARC software architecture pattern
- **sparkle**: structurizing the inputs field in pipeline decorator
- add base interface for spark app

### Fix

- **llm**: block creating api gateway resources on private access
- **spark**: add pyspark to depenedencies to be able to run tests
- **llm**: dependency hierarchy of resources
- **llm**: rename the assume policy method to better naming
- **core**: deprecated id_ parameter leftover
- **controller**: auto provision causing resource creation before before configs
- **factory**: not passing region to aws controllers
- **sparkle**: depricated application paramter for spark controller
- **sparkle**: pin sparkle to v0.3.1 version
- **sparkle**: applications cant be added during controllers init
- **spark**: azure controller not passing applications to parent
- **spark**: make sparkle an optional dependency
- **factory**: tag property not getting initialized properly
- cloud connection creating fully connected dependency graph
- **spark**: creating glue job per pipeline
- **object_storage**: ARC new interface were not supporting
- circular import for type annotations

## 0.3.0 (2024-08-02)

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

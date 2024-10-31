## v0.8.0 (2024-10-31)

### Feat

- **core, llm**: cost managements supports within controllers
- **core, llm**: add supporting tags
- **llm**: remove openai chat method for a native method
- **llm**: make the llm controller support hosting the scripts as well
- **resources**: add new component for serving python applications

### Fix

- **test**: making the test pipeline working
- **llm**: secret key connot be found
- **llm**: cannon recreate secrets after destroying
- **serverless**: pushing empty dependency packages to lambda layer
- **llm**: lambda function does not have access to ssm or secrets
- **llm**: cannot access the api key
- **llm**: endpoint parameter store not being created
- **core**: seprating run/build time dependencies
- **llm**: force set the region for the boto3 client
- **py-serverless**: unable to deploy with dependency bigger than 250mb

### Refactor

- **serverless**: uploading dependencies directly to lambda
- **llm**: using code mode instead of docker mode with lambda
- **llm**: revert back python serverless to lambda layer
- seprating build time and runtime dependencies
- change lambda_component name to serverless_python_component

## v0.7.0 (2024-10-14)

### Feat

- add Java for running spark related applications
- add Job schedule and checkpoints bucket
- work on Glue component

### Fix

- Pulumi args
- application example

### Refactor

- force creating required buckets
- apply PR reviews
- Fix comments and types
- fix format

## v0.6.0 (2024-10-10)

### Feat

- **vllm**: Allow for API key and corresponding usage plan when API is not public
- **AwsVllmComponent**: Add AWS Cognito as authentication service for LLM applications
- **vllm**: Allow for API key and corresponding usage plan when API is not public
- **vllm**: Allow for API key and corresponding usage plan when API is not public
- **AwsVllmComponent**: Add AWS Cognito as authentication service for LLM applications
- **vllm**: Store API key in secrets manager, and create default usage plan for API key
- **AwsVllmComponent**: Add AWS Cognito as authentication service for LLM applications

### Fix

- tests
- tests
- **vllm**: Ensure appropriate errors are raised

### Refactor

- **AwsVllmComponent**: Require an API key when access is not for public internet

## v0.5.0 (2024-10-07)

### Feat

- **core**: add environment and execution mode property to base controller
- **llm**: add llm base controller and aws controller
- **vllm**: saving endpoint base url in parameter store

### Fix

- **llm**: move the cloud agnostic methods of the controller to the base
- **core**: broken import after clean up __init__ files
- **llm, example**: pulumi only works with `__main__.py` file name
- **core**: init all controllers when using `from damavand...controllers`
- **vllm**: make api route open ai compatible

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

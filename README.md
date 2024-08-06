# Damavand

<p align="center">
  <img src="docs/assets/damavand-logo-inverted.png" width="100" height="100""/>
</p>

## What is Damavand?

Damavand is a cloud-agnostic Infrastructure from Code (IfC) library natively written in Python. It allows developers to focus on their area of expertise and leave the infrastructure as code (IaC) development and designing of cloud-native microservice architecture to the framework. Damavand leverages the CDKTF framework and tools to generate Terraform code, ensuring best practices and cloud optimization without vendor lock-in.

## Why Damavand?

Cloud infrastructure can be complex and time-consuming to manage. Damavand simplifies this process by allowing developers to use their existing programming skills to build cloud-native applications. Here are some reasons why you should consider using Damavand:

- **Cloud Complexity**: Simplifies the intricate and ever-evolving landscape of cloud services.
- **Scarcity of Expertise**: Mitigates the need for specialized cloud knowledge, making it easier to manage and deploy cloud infrastructure.
- **Efficiency**: Reduces development time, resulting in faster time to market.
- **Vendor Independence**: Avoids vendor lock-in with multi-cloud support.
- **Unified Context**: Maintains a shared context between application logic and infrastructure code.


## How to Use Damavand?

To use Damavand, all you need is to have Python installed. The framework is designed to be straightforward, enabling developers to set up and deploy cloud application with minimal cloud knowledge.

### Example

Below is a simple example demonstrating how to use Damavand to create a bucket and a Flask server:

```python
from damavand.core import CloudConnection

cloud = CloudConnection.from_aws_provider(
    "my-app",
    region="eu-west-1",
)

my_bucket = cloud.resource_factory.new_bucket(
    "MyLovelyBucket",
    tags={"owner": "kiarash@datachef.co"},
)

my_tiny_server = cloud.resource_factory.new_flask_server(
    __name__,
    name="my-tiny-server",
    tags={"owner": "kiarash@datachef.co"},
)

@my_tiny_server.route("/")
def index():
    return "Hello, World!"

@my_tiny_server.route("/objects/hello")
def hello():
    my_bucket.add_object(b"Hello, World!", "hello.txt")
    return my_bucket.get_object("hello.txt")

cloud.run()
```

## Damavand Features

- **Native Python Implementation**: Fully written in Python with no extra dependencies.
- **Multi-Cloud Targets**: Supports multiple cloud providers, ensuring no vendor lock-in.
- **CDKTF Integration**: Leverages CDKTF framework for generating Terraform code.
- **Native Access**: Provides native access to CDK objects and APIs for fine-grained control.

## What is it Useful For?
Damavand is ideal for:

- **Startups and Small Businesses**: Simplifies cloud infrastructure management during early stages of growth.
- **Large Enterprises**: Optimizes cloud usage and reduces costs across multiple teams and departments.
- **Developers**: Allows developers to manage infrastructure using familiar programming paradigms without delving into low-level cloud configurations.

## What is this Not Useful For?

While Damavand can significantly streamline cloud infrastructure management, it is not a replacement for cloud landing zone platforms. Users still need to make informed decisions about how to manage their cloud infrastructure within a landing zone.

## Supported Languages

Damavand is developed using Python and currently supports Python as the primary language. We are not aming for supporting any other language in near future. The idea is to remain close to Python to benefits from features of python that may or may not be available in other languages.

## Getting Help

If you have any question, issue, or need a feature, please feel free to open an issue on the Damavand GitHub repository. We are always happy to help and improve the framework based on user feedback. If you wonder how you can use it in your organization feel free to reach out to us using [support@datachef.co](mailto:support@datachef.co).

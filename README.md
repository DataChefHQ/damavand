# Damavand

<p align="center">
  <img src="docs/assets/damavand-logo-inverted.png" width="100" height="100""/>
</p>

## What is Damavand?
Damavand is a comprehensive cloud-native application development framework designed to go beyond traditional Infrastructure as Code (IaC). It simplifies both application logic and cloud infrastructure management, providing developers with a unified, Pythonic approach to building, deploying, and scaling cloud-native applications. Damavand implements the ARC (Application, Resource, Controller) design pattern, ensuring that your cloud resources and application logic work seamlessly together without the complexity of deeply understanding cloud provider-specific details.

With Damavand, your focus remains on writing business logic while the framework handles cloud architecture, leveraging Pulumi to generate cloud infrastructure code for multi-cloud environments.

## Why Damavand?
Damavand is built for developers who want to focus on writing applications, not spending countless hours configuring and managing infrastructure. Here’s why Damavand stands out:

- Unified Application and Infrastructure: Develop both cloud resources and business applications in a unified codebase with a clean, logical structure.
- ARC Design Pattern: Follow the proven Application, Resource, and Controller pattern to keep code organized, scalable, and maintainable.
- Best Practices and Flexibility: Offers optimized architecture designs while allowing developers to customize each part of the framework when needed.
- Vendor Independence: Support for multiple cloud providers, avoiding vendor lock-in and giving you the freedom to deploy anywhere.
- Rapid Time-to-Market: Dramatically shortens the time it takes to build and deploy cloud-native applications through pre-architected, cloud-agnostic templates and patterns.

## How Damavand Works

Damavand empowers developers to handle both the application layer and resource layer within one framework. By following the ARC design pattern, it decouples business logic from cloud complexities, enabling easy customization and scalability across different cloud providers.

### Example

Here's an example using Damavand to create an S3 bucket and deploy a simple Flask server:

```python
import os
from damavand.cloud.provider import AwsProvider
from damavand.factories import SparkControllerFactory

from applications.orders import CustomerOrders
from applications.products import Products


def main() -> None:
    spark_factory = SparkControllerFactory(
        provider=AwsProvider(
            app_name="my-app",
            region="us-west-2",
        ),
        tags={"env": "dev"},
    )

    spark_controller = spark_factory.new(
        name="my-spark",
        applications=[
            Products(),
            CustomerOrders(),
        ],
    )

    app_name = os.getenv("APP_NAME", "default_app")  # Get app name on runtime

    spark_controller.provision()
    spark_controller.run_application(app_name)


if __name__ == "__main__":
    main()
```

> [!TIP]
> Checkout the [examples](examples) directory for more examples.

## Key Features
- ARC Design Pattern: Implements the Application, Resource, and Controller layers to streamline the development process.
- Pulumi-Powered IaC: Uses Pulumi to manage cloud infrastructure resources in a cloud-agnostic way, reducing complexity.
- Multi-Cloud Support: Enables you to build applications that can run on AWS, Azure, and more, avoiding vendor lock-in.
- Pythonic Flexibility: Written natively in Python, Damavand allows you to easily modify and extend the framework to meet your application's needs.
- No Extra Dependencies: Requires only the Pulumi CLI for cloud infrastructure management—no unnecessary dependencies.

## What is Damavand Useful For?

Damavand is perfect for:

- Startups: Accelerate the development and deployment of cloud-native applications.
- Enterprises: Ensure scalability, maintainability, and flexibility in cloud applications.
- Developers: Damavand allows you to focus on your expertise—whether it's backend development, data engineering, or another area—without worrying about the complexities of cloud architecture. For advanced users, it provides rich layers of customization to push the boundaries of optimizing solutions for specific cloud providers.

## What Damavand is Not

Damavand is not just an Infrastructure as Code (IaC) tool. It is not meant to be a full-fledged cloud platform, but rather a framework that integrates both application development and cloud infrastructure in a seamless, unified approach.

## Supported Languages

Damavand is developed in Python, with a focus on Python developers looking for a flexible, yet powerful framework for building cloud-native applications.

## Getting Help

For support, issues, or feature requests, please open an issue on the Damavand GitHub repository or contact us at support@datachef.co. We're here to help you build your next cloud-native application efficiently and effectively!

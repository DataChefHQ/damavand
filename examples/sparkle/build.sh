#!/bin/bash

pip install -r requirements.txt --target dependencies/
python setup.py bdist_wheel --dist-dir artifacts
aws s3 cp artifacts/damavand_packages-0.1-py3-none-any.whl s3://my-spark-code-bucket20241009085845037400000001

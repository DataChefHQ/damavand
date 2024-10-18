from setuptools import setup, find_packages

setup(
    name="damavand-packages",
    version="0.1",
    packages=find_packages(where="dependencies"),
    package_dir={"": "dependencies"},
    package_data={
        "": ["*"],
    },
    include_package_data=True,
    zip_safe=False,
)

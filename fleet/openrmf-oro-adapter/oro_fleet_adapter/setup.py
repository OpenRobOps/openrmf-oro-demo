import os
from glob import glob

from setuptools import find_packages, setup

package_name = "oro_fleet_adapter"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name),
            glob("*.config.yaml"),
        ),
        (
            os.path.join("share", package_name, "launch"),
            glob("launch/*.launch.xml"),
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="santiago",
    maintainer_email="santiago.barragan@ekumenlabs.com",
    description="A template for an RMF fleet adapter",
    license="Apache License 2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": ["fleet_adapter=oro_fleet_adapter.fleet_adapter:main"],
    },
)

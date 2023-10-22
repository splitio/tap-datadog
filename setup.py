#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="tap-datadog",
    version="0.2.0",
    description="Singer.io tap for extracting datadog billing data.",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap-datadog"],
    install_requires=[
        "singer-python>=5.0.12",
        "requests",
        "pendulum"
    ],
    entry_points="""
        [console_scripts]
        tap-datadog=tap_datadog:main
    """,
    packages=find_packages(),
    package_data={
          'tap_datadog': [
              'schemas/*.json'
          ]
      }
)

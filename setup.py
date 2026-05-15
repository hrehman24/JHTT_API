"""Minimal setuptools configuration.

Most metadata is in pyproject.toml. This file is kept for compatibility
with older tools and to ensure setuptools generates proper package metadata
during wheel builds.
"""

from setuptools import setup, find_packages

setup(
    name="beatify-api",
    version="0.1.0",
    packages=find_packages(include=["Beatify*"]),
    python_requires=">=3.10",
)

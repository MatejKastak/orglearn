#!/usr/bin/env python

import typing

from setuptools import find_packages, setup


def requirements(filepath: str) -> typing.List[str]:
    """Read requirements from a filepath."""
    res = []
    with open(filepath, "r") as requirements_file:
        for line in requirements_file.readlines():
            res.append(line.strip())
    return res


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="orglearn",
    version="1.0.3",  # TODO: Better way to handle versions
    author="Matej Kastak",
    author_email="matej.kastak@gmail.com",
    description="Tool to learn from your org-mode notes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License ",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Education",
    ],
    include_package_data=True,
    install_requires=requirements("requirements.txt"),
    url="https://github.com/MatejKastak/orglearn",
    packages=find_packages(),
    entry_points={"console_scripts": ["orglearn = orglearn.cli:main"]},
)

#!/usr/bin/env python

from setuptools import setup, find_packages


def requirements(filepath):
    res = []
    with open(filepath, "r") as requirements:
        for line in requirements.readlines():
            res.append(line.strip())
    return res


long_description = """Orglean provides tools for learning from org-mode notes. It can generate mind maps and anki decks."""

setup_info = dict(
    name="orglearn",
    version="0.0.1",  # TODO(mato): Better way to handle versions
    author="Matej Kastak",
    author_email="matej.kastak@gmail.com",
    description="Tool to learn from your org-mode notes",
    long_description=long_description,
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
    packages=find_packages(),
    entry_points={"console_scripts": ["orglearn = orglearn.cli:main"]},
)

setup(**setup_info)

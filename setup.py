import sys
from setuptools import setup, find_packages

with open(r"README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


def get_install_requires():
    req = ["dill>=0.3.5"]

    if sys.version_info.minor < 8:
        req.append("pickle5>=0.0.12")

    return req


setup(
    name="checkpointing",
    version="0.1.1",
    author="Vopaaz",
    author_email="liyifan945@gmail.com",
    url="https://github.com/Vopaaz/checkpointing",
    description="Persistent cache for Python functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=get_install_requires(),
    python_requires=">=3.7, <=3.10",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
)

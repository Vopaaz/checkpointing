from setuptools import setup, find_packages

with open(r"README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="checkpointing",
    version="0.0.2",
    author="Vopaaz",
    author_email="liyifan945@gmail.com",
    url="https://github.com/Vopaaz/checkpointing",
    description="WIP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)

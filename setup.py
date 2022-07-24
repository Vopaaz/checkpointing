from setuptools import setup, find_packages

with open(r"README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="checkpointing",
    version="0.0.5",
    author="Vopaaz",
    author_email="liyifan945@gmail.com",
    url="https://github.com/Vopaaz/checkpointing",
    description="WIP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "dill>=0.3.5",
    ],
    python_requires=">=3.7, <=3.10",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)

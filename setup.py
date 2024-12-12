from setuptools import setup, find_packages
from os import path

loc = path.abspath(path.dirname(__file__))

with open(loc + "/requirements.txt") as f:
    requirements = f.read().splitlines()

required = []
dependency_links = []

# Do not add to required lines pointing to Git repositories
EGG_MARK = "#egg="
for line in requirements:
    if (
        line.startswith("-e git:")
        or line.startswith("-e git+")
        or line.startswith("git:")
        or line.startswith("git+")
    ):
        line = line.lstrip("-e ")  # in case that is using "-e"
        if EGG_MARK in line:
            package_name = line[line.find(EGG_MARK) + len(EGG_MARK) :]
            repository = line[: line.find(EGG_MARK)]
            required.append("%s @ %s" % (package_name, repository))
            dependency_links.append(line)
        else:
            print("Dependency to a git repository should have the format:")
            print("git+ssh://git@github.com/xxxxx/xxxxxx#egg=package_name")
    else:
        required.append(line)

setup(
    name="MediaManager",
    version="1.1.0",
    packages=find_packages(),
    install_requires=required,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    scripts=["bin/mediamanager"],
    author="Ed Salisbury",
    author_email="ed.salisbury@gmail.com",
    description="A tool for managing photo and video files.",
    license="MIT",
    url="https://github.com/edsalisbury/MediaManager",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

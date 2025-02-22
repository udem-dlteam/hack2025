from setuptools import setup, find_packages
import sys
import os

setup(
    name="radar",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],  # Add any dependencies here
    py_modules=["radar", "geodetic"],
    author="Gauransh Kumar",
    author_email="gauranshk21@gmail.com",
    description="A Python package for showing FlightGear data on a live map",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/udem-dlteam/hack2025",  # Change accordingly
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "radar=radar:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["LOWI.png", "radar.css", "radar.html", "radar.js"],  # Include static files
    },
    zip_safe=False,
)

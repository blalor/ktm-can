# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="ktm-can",
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    python_requires=">=3.8",
    install_requires=[
        # eg: "aspectlib==1.1.1", "six>=1.7",
        # "gpxpy>=1.4.2, <2.0",
    ],
    # setup_requires=[
    #     "pytest",
    # ],
)

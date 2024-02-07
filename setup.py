from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="qstrader",
    version="0.2.4",
    description="QSTrader backtesting simulation engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mhallsmoore/qstrader",
    author="Michael Halls-Moore",
    author_email="support@quantstart.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "Click==7.1.2",
        "matplotlib>=3.8.2",
        "numpy>=1.26.4",
        "pandas>=2.2.0",
        "seaborn>=0.13.2"
    ]
)

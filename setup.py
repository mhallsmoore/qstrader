from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="qstrader",
    version="0.1.0",
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
	"Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
	"Click==7.1.2",
	"matplotlib==3.2.1",
        "numpy==1.18.4",
	"pandas==1.0.3",
	"seaborn==0.10.1"
    ]
)


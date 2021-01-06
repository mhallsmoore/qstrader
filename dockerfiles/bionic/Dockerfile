# BUILD:  docker build -t qstrader-bionic .
# RUN:    docker run -it -v "$PWD":/qstrader-data qstrader-bionic

FROM ubuntu:bionic

RUN apt-get update && apt-get install -y git python3-pip
RUN git clone https://github.com/mhallsmoore/qstrader.git
RUN pip3 install -r qstrader/requirements/base.txt
RUN pip3 install -r qstrader/requirements/tests.txt
WORKDIR /qstrader
ENV PYTHONPATH /qstrader
RUN pytest

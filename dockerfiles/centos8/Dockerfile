# BUILD:  docker build -t qstrader-centos8 .
# RUN:    docker run -it -v "$PWD":/qstrader-data qstrader-centos8

FROM centos:8

RUN dnf install -y make gcc gcc-c++ git python3-pip python3-devel
RUN git clone https://github.com/mhallsmoore/qstrader.git
RUN pip3 install -r qstrader/requirements/base.txt
RUN pip3 install -r qstrader/requirements/tests.txt
WORKDIR /qstrader
ENV PYTHONPATH /qstrader
RUN pytest

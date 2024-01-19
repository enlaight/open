FROM ubuntu:20.04

ENV LANG C.UTF-8
RUN apt-get update -y --fix-missing
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get install -y libssl-dev
RUN apt-get install -y libpq-dev
RUN apt-get install -y git
RUN apt-get install -y curl
RUN apt-get install -y python3.9
RUN apt-get install -y python3.9-dev
RUN apt-get install -y python3-pip
RUN apt-get install -y build-essential
RUN apt-get install -y libfontconfig1
RUN apt-get install -y libfontconfig1-dev
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y llvm-10*
RUN apt-get clean all

ADD ./ /root
WORKDIR /root

# Copy and install everything from the requirements file
COPY ./requirements.txt ./requirements.txt
RUN cat requirements.txt | xargs -n 1 pip3 install || true
RUN rm ./requirements.txt